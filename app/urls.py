from django.urls import path, include
from rest_framework import routers
from .views import *
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register(r'applications', ApplicationViewSet)
router.register(r'submittedApplications', SubmittedApplicationViewSet)
router.register(r'funders', FunderViewSet)
router.register(r'pdfs', PDdfsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api/submittedApplications/<str:application_id>/',
         get_submitted_applications, name='get_submitted_applications'),
    path('api/get_starts/',
         get_starts, name='get_starts'),
    path('api/applications/<str:application_id>/pdfs/',
         get_application_pdfs, name='get_application_pdfs'),
    path('api/pdf/<int:id>/', update_pdf_data, name='update_pdf_data'),
    path('get_file/<str:application_id>/<str:pdf_type>/',
         get_file, name="get_file"),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='getAuthUserView'),
    path('api/getcurrentuser/', GetAuthUserView.as_view(), name='getcurrentuser'),
    
#     path('token/',
#          jwt_views.TokenObtainPairView.as_view(),
#          name='token_obtain_pair'),
#     path('token/refresh/',
#          jwt_views.TokenRefreshView.as_view(),
#          name='token_refresh')
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = router.urls
