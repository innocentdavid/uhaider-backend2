from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'status', StatusViewSet)
router.register(r'pdfs', PDdfsViewSet)
# router.register(r'movies', MovieViewSet, basename='movie')

# urlpatterns = [
#     path('', include(router.urls)),
# ]

urlpatterns = router.urls
