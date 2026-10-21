from rest_framework.routers import DefaultRouter
from .views import VacancyViewSet, ApplicationViewSet, RecommendationViewSet

router = DefaultRouter()
router.register('vacancies', VacancyViewSet, basename='vacancy')
router.register('applications', ApplicationViewSet, basename='application')
router.register('recommendations', RecommendationViewSet, basename='recommendation')

urlpatterns = router.urls
