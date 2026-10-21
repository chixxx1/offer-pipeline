from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
import datetime

from apps.tracker.models import Vacancy, VacancyRecommendation
from apps.tracker.services.matching import (
    build_search_query_from_profile,
    calculate_vacancy_match,
    sync_user_recommendations,
)
from apps.users.models import Profile, Skill, ProfileVariant, WorkExperience


def make_skill(name):
    return Skill.get_or_create_normalized(name)


class MatchingServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass')
        self.profile = Profile.get_for_user(self.user)
        self.profile.city = 'Москва'
        self.profile.desired_salary = 150000
        self.profile.work_format = 'remote'
        self.profile.save()

        self.skill_python = make_skill('Python')
        self.skill_django = make_skill('Django')
        self.skill_go = make_skill('Go')
        self.profile.skills.set([self.skill_python, self.skill_django])

    def test_build_search_query_prioritizes_skills(self):
        params = build_search_query_from_profile(self.profile)
        # Навыки нормализуются в нижний регистр и сортируются по алфавиту.
        self.assertEqual(params['text'], 'django python')
        self.assertEqual(params['order_by'], 'publication_time')
        self.assertEqual(params['page'], 0)
        self.assertEqual(params['work_format'], ['remote'])

    def test_build_search_query_fallback_to_position(self):
        # Профиль без навыков, без варианта — фоллбэк на должность.
        empty_user = User.objects.create_user(username='empty', password='pass')
        empty_profile = Profile.get_for_user(empty_user)
        WorkExperience.objects.create(
            profile=empty_profile,
            company='ООО Ромашка',
            position='Middle Python Developer',
            start_date=datetime.date(2020, 1, 1),
            is_current=True,
        )
        params = build_search_query_from_profile(empty_profile)
        self.assertEqual(params['text'], 'Middle Python Developer')

    def test_build_search_query_uses_variant(self):
        variant = ProfileVariant.objects.create(
            profile=self.profile, title='Go Developer'
        )
        variant.skills.set([self.skill_go])
        params = build_search_query_from_profile(self.profile, variant=variant)
        self.assertEqual(params['text'], 'Go Developer')
        self.assertEqual(params['order_by'], 'publication_time')

    def test_calculate_vacancy_match_skills_priority(self):
        vacancy = Vacancy.objects.create(
            title='Python Django Developer',
            company='Tech Co',
            url='https://hh.ru/vacancy/1',
            source='hh.ru',
            location='Москва',
            work_format='remote',
            salary_from=140000,
            salary_to=160000,
        )
        vacancy.skills.set([self.skill_python, self.skill_django])

        match = calculate_vacancy_match(vacancy, self.profile)
        self.assertEqual(set(match['matched_skills']), {'python', 'django'})
        self.assertEqual(match['missing_skills'], [])
        self.assertGreaterEqual(match['score'], 65)  # навыки дают до 65 + остальное
        self.assertIn('Совпадение навыков', ' '.join(match['reasons']))

    def test_calculate_vacancy_match_missing_skills(self):
        vacancy = Vacancy.objects.create(
            title='Go Developer',
            company='Tech Co',
            url='https://hh.ru/vacancy/2',
            source='hh.ru',
            location='Санкт-Петербург',
            work_format='office',
            salary_from=50000,
            salary_to=60000,
        )
        match = calculate_vacancy_match(vacancy, self.profile)
        self.assertEqual(match['matched_skills'], [])
        self.assertEqual(set(match['missing_skills']), {'python', 'django'})
        self.assertEqual(match['score'], 0)

    def test_calculate_vacancy_match_skill_in_title(self):
        # Навык есть в заголовке вакансии, но не в vacancy.skills — должен засчитаться.
        vacancy = Vacancy.objects.create(
            title='Python разработчик',
            company='Tech Co',
            url='https://hh.ru/vacancy/3',
            source='hh.ru',
            location='Москва',
            work_format='remote',
        )
        match = calculate_vacancy_match(vacancy, self.profile)
        self.assertIn('python', match['matched_skills'])
        self.assertNotIn('python', match['missing_skills'])


class SyncRecommendationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='syncer', password='pass')
        self.profile = Profile.get_for_user(self.user)
        self.profile.city = 'Москва'
        self.profile.work_format = 'remote'
        self.profile.save()
        self.skill_python = make_skill('Python')
        self.profile.skills.set([self.skill_python])

    @override_settings(DEBUG=True)
    def test_sync_without_fetch_creates_recommendations(self):
        vacancy = Vacancy.objects.create(
            title='Python Developer',
            company='Tech Co',
            url='https://hh.ru/vacancy/10',
            source='hh.ru',
            location='Москва',
            work_format='remote',
            salary_from=100000,
            salary_to=200000,
        )
        vacancy.skills.set([self.skill_python])

        recs = sync_user_recommendations(self.user, fetch_from_hh=False)
        self.assertTrue(len(recs) >= 1)
        rec = recs[0]
        self.assertTrue(rec.is_new)
        self.assertFalse(rec.is_dismissed)

    @override_settings(DEBUG=True)
    def test_sync_does_not_reset_existing_flags(self):
        vacancy = Vacancy.objects.create(
            title='Python Developer',
            company='Tech Co',
            url='https://hh.ru/vacancy/11',
            source='hh.ru',
            location='Москва',
            work_format='remote',
        )
        VacancyRecommendation.objects.create(
            user=self.user, vacancy=vacancy, score=50,
            is_new=False, is_dismissed=True,
        )
        sync_user_recommendations(self.user, fetch_from_hh=False)
        rec = VacancyRecommendation.objects.get(user=self.user, vacancy=vacancy)
        self.assertFalse(rec.is_new)
        self.assertTrue(rec.is_dismissed)


class RecommendationOrderingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='order', password='pass')
        self.profile = Profile.get_for_user(self.user)
        self.profile.city = 'Москва'
        self.profile.work_format = 'any'
        self.profile.save()
        self.client = APIClient()

        self.v_old = Vacancy.objects.create(
            title='Old Java',
            company='C1', url='https://hh.ru/vacancy/20',
            source='hh.ru', location='Москва', work_format='remote',
        )
        self.v_new = Vacancy.objects.create(
            title='Fresh Python',
            company='C2', url='https://hh.ru/vacancy/21',
            source='hh.ru', location='Москва', work_format='remote',
        )

        self.v_old.published_at = timezone.now() - datetime.timedelta(days=10)
        self.v_old.save()
        self.v_new.published_at = timezone.now() - datetime.timedelta(days=1)
        self.v_new.save()

        VacancyRecommendation.objects.create(
            user=self.user, vacancy=self.v_old, score=90, is_dismissed=False
        )
        VacancyRecommendation.objects.create(
            user=self.user, vacancy=self.v_new, score=10, is_dismissed=False
        )

    def _auth(self):
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_recommendations_ordered_by_freshness(self):
        self._auth()
        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, 200)
        results = response.data
        ids = [r['vacancy']['id'] for r in results]
        # Сначала свежая вакансия, несмотря на более низкий score.
        self.assertEqual(ids[0], self.v_new.id)
        self.assertEqual(ids[1], self.v_old.id)

    def test_only_new_filter(self):
        self._auth()
        # Пометим старую как seen.
        VacancyRecommendation.objects.filter(user=self.user, vacancy=self.v_old).update(is_new=False)
        response = self.client.get('/api/recommendations/?only_new=true')
        self.assertEqual(response.status_code, 200)
        ids = [r['vacancy']['id'] for r in response.data]
        self.assertEqual(ids, [self.v_new.id])

    def test_min_score_filter(self):
        self._auth()
        response = self.client.get('/api/recommendations/?min_score=50')
        self.assertEqual(response.status_code, 200)
        ids = [r['vacancy']['id'] for r in response.data]
        self.assertIn(self.v_old.id, ids)
        self.assertNotIn(self.v_new.id, ids)

    def test_dismissed_excluded(self):
        self._auth()
        VacancyRecommendation.objects.filter(user=self.user, vacancy=self.v_new).update(is_dismissed=True)
        response = self.client.get('/api/recommendations/')
        self.assertEqual(response.status_code, 200)
        ids = [r['vacancy']['id'] for r in response.data]
        self.assertEqual(ids, [self.v_old.id])


class RecommendationActionsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='actor', password='pass')
        self.profile = Profile.get_for_user(self.user)
        self.profile.city = 'Москва'
        self.profile.work_format = 'any'
        self.profile.save()
        self.client = APIClient()
        self.vacancy = Vacancy.objects.create(
            title='Python Developer',
            company='C', url='https://hh.ru/vacancy/30',
            source='hh.ru', location='Москва', work_format='remote',
        )
        self.rec = VacancyRecommendation.objects.create(
            user=self.user, vacancy=self.vacancy, score=50,
            is_new=True, is_dismissed=False,
        )
        token = AccessToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_dismiss(self):
        response = self.client.post(f'/api/recommendations/{self.rec.id}/dismiss/')
        self.assertEqual(response.status_code, 200)
        self.rec.refresh_from_db()
        self.assertTrue(self.rec.is_dismissed)
        self.assertFalse(self.rec.is_new)

        # Дismissed не должна appearing в списке.
        response = self.client.get('/api/recommendations/')
        ids = [r['id'] for r in response.data]
        self.assertNotIn(self.rec.id, ids)

    def test_mark_seen(self):
        response = self.client.post('/api/recommendations/mark-seen/', {'ids': [self.rec.id]}, format='json')
        self.assertEqual(response.status_code, 200)
        self.rec.refresh_from_db()
        self.assertFalse(self.rec.is_new)
