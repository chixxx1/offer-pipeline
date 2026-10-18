import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Profile, ProfileVariant, ResumeFile, Skill, WorkExperience


class MediaRootIsolationMixin:

    def setUp(self):
        self._media_root = tempfile.mkdtemp(prefix='op_test_media_')
        override = override_settings(MEDIA_ROOT=self._media_root)
        override.enable()
        self.addCleanup(override.disable)
        self.addCleanup(shutil.rmtree, self._media_root, True)


class ProfileAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.client.force_authenticate(self.user)

    def test_profile_created_on_first_request(self):
        self.assertFalse(Profile.objects.filter(user=self.user).exists())
        response = self.client.get('/api/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        self.assertEqual(response.data['work_format'], 'any')

    def test_profile_update_with_skills(self):
        response = self.client.patch(
            '/api/profile/',
            {
                'about': 'Python developer',
                'city': 'Москва',
                'desired_salary': 200000,
                'work_format': 'remote',
                'skills': ['  Python ', 'SQL', 'python'],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city'], 'Москва')
        self.assertEqual(response.data['work_format'], 'remote')
        self.assertEqual(sorted(response.data['skills']), ['python', 'sql'])
        self.assertEqual(Skill.objects.filter(name='python').count(), 1)
        self.assertTrue(Skill.objects.filter(name='sql', slug='sql').exists())

    def test_profile_isolated_per_user(self):
        other = User.objects.create_user(username='bob', password='pass12345')
        self.client.patch('/api/profile/', {'city': 'Казань'}, format='json')
        self.client.force_authenticate(other)
        response = self.client.get('/api/profile/')
        self.assertEqual(response.data['city'], '')

    def test_skills_autocomplete(self):
        Skill.objects.create(name='python')
        Skill.objects.create(name='pytorch')
        Skill.objects.create(name='django')
        response = self.client.get('/api/skills/', {'q': 'py'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in response.data]
        self.assertIn('python', names)
        self.assertIn('pytorch', names)
        self.assertNotIn('django', names)


class WorkExperienceAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.client.force_authenticate(self.user)
        self.profile = Profile.get_for_user(self.user)

    def test_create_and_update_experience(self):
        response = self.client.post(
            '/api/profile/experiences/',
            {
                'company': 'Yandex',
                'position': 'Backend Developer',
                'start_date': '2022-01-01',
                'end_date': '2024-01-01',
                'is_current': False,
                'description': 'Разработка сервисов',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(WorkExperience.objects.filter(profile=self.profile).count(), 1)

        experience_id = response.data['id']
        response = self.client.patch(
            f'/api/profile/experiences/{experience_id}/',
            {'is_current': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_current'])
        self.assertIsNone(response.data['end_date'])

    def test_experience_validation(self):
        response = self.client.post(
            '/api/profile/experiences/',
            {
                'company': 'Yandex',
                'position': 'Backend Developer',
                'start_date': '2024-01-01',
                'end_date': '2022-01-01',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('end_date', response.data)

    def test_experience_isolated_per_user(self):
        other = User.objects.create_user(username='bob', password='pass12345')
        other_profile = Profile.get_for_user(other)
        experience = WorkExperience.objects.create(
            profile=other_profile,
            company='Google',
            position='Dev',
            start_date='2020-01-01',
        )
        response = self.client.get(f'/api/profile/experiences/{experience.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProfileVariantAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.client.force_authenticate(self.user)
        self.profile = Profile.get_for_user(self.user)
        self.experience = WorkExperience.objects.create(
            profile=self.profile,
            company='Yandex',
            position='Python Developer',
            start_date='2022-01-01',
            is_current=True,
        )

    def test_create_variant_with_skills_and_experience(self):
        response = self.client.post(
            '/api/profile/variants/',
            {
                'title': 'Python Developer',
                'about': 'Backend разработка',
                'skills': ['Python', 'FastAPI'],
                'experience_ids': [self.experience.id],
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, getattr(response, 'data', None))
        variant = ProfileVariant.objects.get(id=response.data['id'])
        self.assertEqual(variant.skills.count(), 2)
        self.assertIn(self.experience, variant.experiences.all())

    def test_variant_cannot_use_foreign_experience(self):
        other = User.objects.create_user(username='bob', password='pass12345')
        other_profile = Profile.get_for_user(other)
        foreign_experience = WorkExperience.objects.create(
            profile=other_profile,
            company='Google',
            position='Go Developer',
            start_date='2021-01-01',
        )
        response = self.client.post(
            '/api/profile/variants/',
            {'title': 'Golang Developer', 'experience_ids': [foreign_experience.id]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_variant_isolated_per_user(self):
        other = User.objects.create_user(username='bob', password='pass12345')
        other_profile = Profile.get_for_user(other)
        variant = ProfileVariant.objects.create(profile=other_profile, title='Dev')
        response = self.client.delete(f'/api/profile/variants/{variant.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ResumeFileAPITestCase(MediaRootIsolationMixin, APITestCase):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='alice', password='pass12345')
        self.client.force_authenticate(self.user)
        self.profile = Profile.get_for_user(self.user)

    def _upload(self, filename='resume.pdf', size=100):
        content = b'x' * size
        file = SimpleUploadedFile(filename, content)
        return self.client.post('/api/profile/resumes/', {'file': file}, format='multipart')

    def test_upload_and_download_by_owner(self):
        response = self._upload()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ResumeFile.objects.count(), 1)
        resume = ResumeFile.objects.first()
        self.assertEqual(resume.original_name, 'resume.pdf')

        download = self.client.get(f'/api/profile/resumes/{response.data["id"]}/')
        self.assertEqual(download.status_code, status.HTTP_200_OK)
        self.assertEqual(download['Content-Disposition'], f'attachment; filename="resume.pdf"')

    def test_upload_invalid_extension(self):
        response = self._upload(filename='resume.txt')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_too_large(self):
        response = self._upload(filename='resume.pdf', size=10 * 1024 * 1024 + 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_download_other_users_resume_denied(self):
        other = User.objects.create_user(username='bob', password='pass12345')
        other_profile = Profile.get_for_user(other)
        file = SimpleUploadedFile('resume.pdf', b'pdf-content')
        resume = ResumeFile.objects.create(
            profile=other_profile,
            file=file,
            original_name='resume.pdf',
        )
        response = self.client.get(f'/api/profile/resumes/{resume.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_removes_file(self):
        response = self._upload()
        resume_id = response.data['id']
        resume = ResumeFile.objects.get(id=resume_id)
        file_path = resume.file.path
        delete_response = self.client.delete(f'/api/profile/resumes/{resume_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(os.path.exists(file_path))
        self.assertEqual(ResumeFile.objects.count(), 0)
