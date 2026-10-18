from django.http import FileResponse
from rest_framework import generics, permissions, viewsets
from rest_framework.views import APIView

from .models import Education, Profile, ProfileVariant, ResumeFile, Skill, WorkExperience
from .serializers import (
    EducationSerializer,
    ProfileSerializer,
    ProfileVariantSerializer,
    ResumeFileSerializer,
    SkillSerializer,
    WorkExperienceSerializer,
)


class ProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def get_object(self):
        return Profile.get_for_user(self.request.user)
        


class ProfileChildViewSetMixin:

    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(profile=Profile.get_for_user(self.request.user))


class WorkExperienceViewSet(ProfileChildViewSetMixin, viewsets.ModelViewSet):
    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        return WorkExperience.objects.filter(profile__user=self.request.user)


class EducationViewSet(ProfileChildViewSetMixin, viewsets.ModelViewSet):
    serializer_class = EducationSerializer

    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user)


class ProfileVariantViewSet(ProfileChildViewSetMixin, viewsets.ModelViewSet):
    serializer_class = ProfileVariantSerializer

    def get_queryset(self):
        return ProfileVariant.objects.filter(profile__user=self.request.user)


class SkillListView(generics.ListAPIView):

    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Skill.objects.all()
        query = self.request.query_params.get('q', '').strip()
        if query:
            queryset = queryset.filter(name__icontains=query.lower())
        return queryset


class ResumeFileViewSet(viewsets.ModelViewSet):

    serializer_class = ResumeFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        return ResumeFile.objects.filter(profile__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(profile=Profile.get_for_user(self.request.user))

    def _get_owned_resume(self) -> ResumeFile:
        resume = generics.get_object_or_404(ResumeFile, pk=self.kwargs['pk'])
        if resume.profile.user != self.request.user:
            from rest_framework.exceptions import NotFound
            raise NotFound('Файл резюме не найден.')
        return resume

    def retrieve(self, request, *args, **kwargs):
        resume = self._get_owned_resume()
        return FileResponse(
            resume.file.open('rb'),
            as_attachment=True,
            filename=resume.original_name,
            content_type='application/octet-stream',
        )
