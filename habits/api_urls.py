from rest_framework.routers import DefaultRouter
from .api import HabitViewSet

router = DefaultRouter()
router.register(r'habits', HabitViewSet, basename='habit')

urlpatterns = router.urls