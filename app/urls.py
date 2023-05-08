from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'status', StatusViewSet)
router.register(r'pdfs', PDdfsViewSet)
# router.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = [
    path('', include(router.urls)),
    path('api/applications/<str:application_id>/pdfs/',
         get_application_pdfs, name='get_application_pdfs'),
    path('applications/<str:application_id>/update/',
         update_application, name="update_application"),
]

# urlpatterns = router.urls
