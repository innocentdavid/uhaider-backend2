from django.shortcuts import get_object_or_404
# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, parsers, generics, views
# from requests import Response
from rest_framework import status, exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from django.http import HttpResponse
from .models import *
from .serializers import *
import base64
import tempfile
import PyPDF2
from django.views.decorators.csrf import csrf_exempt
import jwt
import datetime
from django.db.models import Sum


def has_permission_b(request):
    token = request.COOKIES.get('jwt', None)
    if not token:
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header is not None and auth_header.startswith('Bearer '):
            if auth_header[7:] != 'undefined':
                token = auth_header[7:]

    if token is None:
        return False
    try:
        payload = jwt.decode(token, 'secret', algorithms=["HS256"])
    except jwt.exceptions.DecodeError:
        return False
    except jwt.exceptions.InvalidSignatureError:
        return False
    except jwt.exceptions.ExpiredSignatureError:
        return False
    except:
        return False
    return True
        

class HasTokenCookiePermission(BasePermission):
    def has_permission(self, request, view):
        return has_permission_b(request=request)
        # token = request.COOKIES.get('jwt', None)
        # if not token:
        #     auth_header = request.META.get('HTTP_AUTHORIZATION')
        #     if auth_header is not None and auth_header.startswith('Bearer '):
        #         print(auth_header)
        #         if auth_header[7:] != 'undefined':
        #             token = auth_header[7:]
                    
        # if token is None:
        #     return False
        # return True


class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        payload = {
            'id': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        #    .decode('utf-8')
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=False)

        response_data = serializer.data
        # response_data['jwt'] = token
        response_data['message'] = "success"
        response.data = response_data
        # response.status
        return response

        # return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = CustomUser.objects.filter(email=email).first()

        if user is None:
            return Response({"message": "User not found"})

        if not user.check_password(password):
            return Response({"message": "Password incorrect"})

        payload = {
            'id': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        # .decode('utf-8')
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=False)
        response.data = {"message": 'success'}
        return response

        # return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetAuthUserView(views.APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        # print(token)
        if token is None:
            return Response({"message": "Unauthenticated!"})
        try:
            payload = jwt.decode(token, 'secret', algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            return Response({"message": "Invalid signature!"})
        except jwt.exceptions.ExpiredSignatureError:
            return Response({"message": "Signature has expired!"})
        except jwt.exceptions.DecodeError:
            return Response({"message": "Invalid token!"})
        except:
            return Response({"message": "Unauthenticated!"})

        try:
            user = CustomUser.objects.filter(email=payload['id']).first()
            serializer = UserSerializer(user)
            response_data = serializer.data
            response_data['message'] = 'success'
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response({"message", "Unsuccessful!"})


class LogoutView(views.APIView):
    def post(self, request):
        response = HttpResponse()
        response.delete_cookie('jwt')
        response.set_cookie('jwt', '', expires=0, httponly=False)
        response.data = {
            'message': 'success'
        }
        return response


def get_application_pdfs(request, application_id):
    permission_classes = has_permission_b(request=request)
    if not permission_classes:
        return JsonResponse({"message": "Unauthorized!"}, status=status.HTTP_401_UNAUTHORIZED)
        
    try:
        application = Application.objects.get(application_id=application_id)
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Application not found.'}, status=404)

    pdfs = PdfFile.objects.filter(
        application__application_id=application_id)

    # pdf_urls = [pdf.file.url for pdf in pdfs]

    pdf_data = []
    for pdf in pdfs:
        application = pdf.application
        pdf_data.append({
            # "pdf_file": pdf.file,
            "pdf_urls": pdf.file.url,
            'pdf_type': pdf.pdf_type,
            'business_name': pdf.business_name,
            'bank_name': pdf.bank_name,
            'begin_bal_date': pdf.begin_bal_date,
            'begin_bal_amount': pdf.begin_bal_amount,
            'total_deposit': pdf.total_deposit,
            'ending_bal_date': pdf.ending_bal_date,
            'ending_bal_amount': pdf.ending_bal_amount
        })

    return JsonResponse({'pdfs': pdf_data})


class FunderViewSet(viewsets.ModelViewSet):
    serializer_class = FunderSerializer
    queryset = Funder.objects.all()
    permission_classes = [HasTokenCookiePermission]


class PDdfsViewSet(viewsets.ModelViewSet):
    serializer_class = PdfFileSerializer
    queryset = PdfFile.objects.all()
    permission_classes = [HasTokenCookiePermission]
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def create(self, request, *args, **kwargs):
        if not 'pdf_type' in request.data:
            return Response({"message": "pdf_type is missing"}, status=status.HTTP_400_BAD_REQUEST)
        if not 'application_id' in request.data:
            return Response({"message": "application_id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        if not 'pdf_file' in request.data:
            return Response({"message": "pdf_file is missing"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_type = request.data['pdf_type']
        application_id = request.data['application_id']
        pdf_file = request.data['pdf_file']

        business_name = ""
        bank_name = ""
        begin_bal_amount = ""
        begin_bal_date = ""
        ending_bal_amount = ""
        ending_bal_date = ""
        total_deposit = ""

        try:
            business_name = request.data['business_name']
            bank_name = request.data['bank_name']
            total_deposit = request.data['total_deposit']
            begin_bal_amount = request.data['begin_bal_amount']
            begin_bal_date = request.data['begin_bal_date']
            ending_bal_amount = request.data['ending_bal_amount']
            ending_bal_date = request.data['ending_bal_date']
        except:
            pass

        application = Application.objects.filter(
            application_id=application_id).first()

        if not application:
            return Response({"message": "application not found"}, status=status.HTTP_404_NOT_FOUND)

        pdfFile = PdfFile.objects.create(
            file=pdf_file,
            pdf_type=pdf_type,
            business_name=business_name,
            bank_name=bank_name,
            begin_bal_amount=begin_bal_amount,
            begin_bal_date=begin_bal_date,
            ending_bal_amount=ending_bal_amount,
            ending_bal_date=ending_bal_date,
            total_deposit=total_deposit,
        )
        pdfFile.application_id = application
        pdfFile.save()

        return Response(status=status.HTTP_201_CREATED)


def get_file(request, application_id, pdf_type):
    permission_classes = has_permission_b(request=request)
    if not permission_classes:
        response_text = 'Unauthorized!'
        return HttpResponse(response_text, status=status.HTTP_401_UNAUTHORIZED)
        
    pdf_file = get_object_or_404(
        PdfFile, application_id=application_id, pdf_type=pdf_type)
    response = HttpResponse(pdf_file.file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
    return response
    # file_path = os.path.join(settings.MEDIA_ROOT, 'pdf_files', filename)
    # if os.path.exists(file_path):
    #     with open(file_path, 'rb') as f:
    #         file_content = f.read()
    #     response = HttpResponse(file_content, content_type='application/pdf')
    #     response['Content-Disposition'] = f'attachment; filename="{filename}"'
    #     return response
    # else:
    #     return HttpResponse('File not found', status=404)


def get_submitted_applications(request, application_id):
    permission_classes = has_permission_b(request=request)
    if not permission_classes:
        return JsonResponse({"message": "Unauthorized!"}, status=status.HTTP_401_UNAUTHORIZED)
        
    submitted_applications = SubmittedApplication.objects.filter(
        application_id=application_id)

    serialized_application = SubmittedApplicationSerializer(
        submitted_applications, many=True)

    return JsonResponse(serialized_application.data, safe=False, status=status.HTTP_200_OK)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    permission_classes = [HasTokenCookiePermission]

    def create(self, request, *args, **kwargs):
        serializer = ApplicationSerializer(data=request.data)
        # print(serializer.is_valid())
        if serializer.is_valid():
            application = Application(**serializer.validated_data)
            application_id = application.application_id
            total_count = Application.objects.count()
            application.count = total_count+1
            application.save()

            response_data = serializer.data
            response_data['application_id'] = application_id
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(status=status.HTTP_201_CREATED)


class SubmittedApplicationViewSet(viewsets.ModelViewSet):
    queryset = SubmittedApplication.objects.all()
    serializer_class = SubmittedApplicationSerializer
    permission_classes = [HasTokenCookiePermission]

    def create(self, request, *args, **kwargs):
        serializer = SubmittedApplicationSerializer(data=request.data)

        if serializer.is_valid():
            if not 'funder_names' in request.data:
                return Response({"message": "funder not selected"}, status=status.HTTP_400_BAD_REQUEST)
            funder_names = request.data['funder_names']
            for funder_name in funder_names:
                funder = Funder.objects.filter(
                    name=funder_name['name']).first()
                if not funder:
                    return Response({"message": "funder not found"}, status=status.HTTP_404_NOT_FOUND)
                submittedApplication = SubmittedApplication(
                    **serializer.validated_data)
                submittedApplication.funder = funder
                submittedApplication.save()
                submittedApplication_id = submittedApplication.application_id

                response_data = serializer.data
                response_data['submittedApplication_id'] = submittedApplication_id

            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(status=status.HTTP_201_CREATED)


def get_application_stats(status_substring):    
    all_apps = SubmittedApplication.objects.filter(
        status__icontains=status_substring)
    app_count = all_apps.count()
    app_sum = all_apps.aggregate(Sum('advanced_price'))[
        'advanced_price__sum'] or 0
    return {'count': app_count, 'sum': app_sum}


def get_starts(request):
    permission_classes = has_permission_b(request=request)
    if not permission_classes:
        return JsonResponse({"message": "Unauthorized!"}, status=status.HTTP_401_UNAUTHORIZED)
        
    response_data = {}
    all_approved_apps = SubmittedApplication.objects.filter(
        status__icontains='approved')
    app_count = all_approved_apps.count()
    app_sum = all_approved_apps.aggregate(Sum('payment'))[
        'payment__sum'] or 0
    commission_price_from_all_approved_apps_sum = all_approved_apps.aggregate(Sum('commission_price'))[
        'commission_price__sum'] or 0
    approved = {'count': app_count, 'sum': app_sum}

    try:
        percentage = round(
            (app_sum / commission_price_from_all_approved_apps_sum)*100, 2)
    except:
        percentage = 0

    commission = {'count': app_count,
                  'sum': commission_price_from_all_approved_apps_sum, 'percentage': percentage}

    response_data['approved'] = approved
    response_data['commission'] = commission

    status_list = ['awaiting', 'submitted', 'declined', 'funded']
    for status_str in status_list:
        response_data[status_str] = get_application_stats(status_str)
    return JsonResponse(response_data, safe=False, status=status.HTTP_200_OK)
