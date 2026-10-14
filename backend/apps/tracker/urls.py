from rest_framework.routers import DefaultRouter
from .views import VacancyViewSet, ApplicationViewSet

router = DefaultRouter()
router.register('vacancies', VacancyViewSet, basename='vacancy')
router.register('applications', ApplicationViewSet, basename='application')

urlpatterns = router.urls