from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    EducationViewSet,
    ProfileVariantViewSet,
    ProfileView,
    ResumeFileViewSet,
    SkillListView,
    WorkExperienceViewSet,
)

router = DefaultRouter()
router.register('profile/experiences', WorkExperienceViewSet, basename='work-experience')
router.register('profile/education', EducationViewSet, basename='education')
router.register('profile/variants', ProfileVariantViewSet, basename='profile-variant')
router.register('profile/resumes', ResumeFileViewSet, basename='resume-file')

detail_list = router.urls

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('skills/', SkillListView.as_view(), name='skills'),
    *detail_list,
]
