from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'status', StatusViewSet)
router.register(r'pdfs', PDdfsViewSet)
# router.register(r'user', UserViewSet)
# router.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = [
    path('', include(router.urls)),
    path('api/applications/<str:application_id>/pdfs/',
         get_application_pdfs, name='get_application_pdfs'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/getcurrentuser/', GetAuthUserView.as_view(), name='getcurrentuser'),
    path('api/logout/', LogoutView.as_view(), name='getAuthUserView'),
]

# urlpatterns = router.urls
