from django.urls import path, include
from rest_framework import routers
from .views import *
from django.conf import settings
from django.conf.urls.static import static
# from rest_framework_simplejwt import views as jwt_views

router = routers.DefaultRouter()
router.register(r'api/applications', ApplicationViewSet)
router.register(r'api/submittedApplications', SubmittedApplicationViewSet)
router.register(r'api/funders', FunderViewSet)
router.register(r'api/pdfs', PDdfsViewSet)
router.register(r'api/emails', EmailViewSet)
router.register(r'api/latestRecords', LatestRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    #     path('api/pdfs/<str:url>/',
    #          PDdfsViewSet.as_view({'get': 'pdf_view'}), name='2pdf_view'),
    #     path('api/pdfs/pdf_files/<str:url>/',
    #          PDdfsViewSet.as_view({'get': 'pdf_view'}), name='3pdf_view'),
    path('api/pdfs/pdf_files/<str:folder>/<str:url>/',
         PDdfsViewSet.as_view({'get': 'pdf_view'}), name='pdf_view'),
    path('api/get_file/<str:application_id>/<str:pdf_type>/',
         get_file, name="get_file"),
#     path('api/submittedApplications/<str:application_id>/',
#          get_submitted_applications, name='get_submitted_applications'),
    path('api/get_starts/',
         get_starts, name='get_starts'),
    path('api/applications/<str:application_id>/pdfs/',
         get_application_pdfs, name='get_application_pdfs'),
    path('api/pdf/<int:id>/', update_pdf_data, name='update_pdf_data'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='getAuthUserView'),
    path('api/getcurrentuser/', GetAuthUserView.as_view(), name='getcurrentuser'),
    path('api/get_score/<str:application_id>/', get_score, name="get_score"),

    #     path('token/',
    #          jwt_views.TokenObtainPairView.as_view(),
    #          name='token_obtain_pair'),
    #     path('token/refresh/',
    #          jwt_views.TokenRefreshView.as_view(),
    #          name='token_refresh')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns = router.urls
