from rest_framework.routers import DefaultRouter
from .views import VacancyViewSet, ApplicationViewSet

router = DefaultRouter()
router.register('vacancies', VacancyViewSet)
router.register('applications', ApplicationViewSet)

urlpatterns = router.urls