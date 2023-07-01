import time
import base64
import datetime
import jwt
import PyPDF2
import tempfile
import random

from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import exceptions, generics, parsers, status, viewsets, views
from rest_framework.permissions import BasePermission
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import *
from .serializers import *

from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

import datetime
import calendar
from .config import exp_hours


class RegisterView(views.APIView):
    def post(self, request):
        userWithEmail = CustomUser.objects.filter(
            email=request.data['email']).first()
        if userWithEmail is not None:
            return Response({"message": "Registration failed, user with email already registered"}, status=status.HTTP_208_ALREADY_REPORTED)
        userWithName = CustomUser.objects.filter(
            name=request.data['name']).first()
        if userWithName is not None:
            return Response({"message": "Registration failed, user with name already registered"}, status=status.HTTP_208_ALREADY_REPORTED)
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        current_datetime = datetime.datetime.utcnow()
        expiration_time_seconds = current_datetime + \
            datetime.timedelta(hours=exp_hours)
        expiration_timestamp = calendar.timegm(
            expiration_time_seconds.utctimetuple())

        payload = {
            'id': user.email,
            'exp': expiration_timestamp,
            'iat': int(time.time())
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        response = Response()

        response_data = serializer.data
        # response_data['jwt'] = token
        response_data['message'] = "success"
        response_data['token'] = token
        response_data['expiration_time'] = expiration_timestamp
        response.data = response_data
        # response.status
        return response

        # return Response(response_data, status=status.HTTP_201_CREATED)


class LoginView(views.APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'message': 'Please provide both email and password.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({'message': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        current_datetime = datetime.datetime.utcnow()
        # expiration_time_seconds = current_datetime + datetime.timedelta(seconds=20)
        expiration_time_seconds = current_datetime + datetime.timedelta(hours=exp_hours)
        expiration_timestamp = calendar.timegm(expiration_time_seconds.utctimetuple())
        
        # Generate JWT token
        token_payload = {
            'id': user.email,
            'exp': expiration_timestamp,
            'iat': int(time.time())
        }

        token = jwt.encode(
            token_payload, settings.SECRET_KEY, algorithm='HS256')
        user_serializer = UserSerializer(user)

        response_data = {
            'message': 'Login successful.',
            'token': token,
            'expiration_time': expiration_timestamp,
            'user': user_serializer.data  # Include serialized user data in the response
        }

        response = Response(response_data, status=status.HTTP_200_OK)

        return response


class GetAuthUserView(views.APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header is not None and auth_header.startswith('Bearer '):
                if auth_header[7:] != 'undefined':
                    token = auth_header[7:]
            else:
                auth_cookie = request.META.get('HTTP_COOKIE')
                if auth_cookie is not None and auth_cookie.startswith('jwt'):
                    if auth_cookie[4:] != 'undefined':
                        token = auth_cookie[4:]

        if token is None:
            return Response({"message": "Unauthenticated!"})
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms="HS256")
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
        response.delete_cookie(key='jwt')

        return Response({'message': 'You have been logged out.'}, status=status.HTTP_200_OK)


def get_application_pdfs(request, application_id):
    try:
        application = Application.objects.get(application_id=application_id)
    except Application.DoesNotExist:
        return JsonResponse({'error': 'Application not found.'}, status=404)

    pdfs = PdfFile.objects.filter(application__application_id=application_id)

    pdf_data = list(pdfs.values())

    return JsonResponse({'pdfs': pdf_data})


class EmailViewSet(viewsets.ModelViewSet):
    serializer_class = EmailSerializer
    queryset = Email.objects.all()

    def get_queryset(self):
        # Get the value of 'sent' parameter from the request query parameters
        sent_param = self.request.query_params.get('sent')
        if sent_param is not None:
            # Convert to lowercase for case-insensitive comparison
            sent_param = sent_param.lower()

            if sent_param == 'true':
                sent_param = True
            elif sent_param == 'false':
                sent_param = False
            else:
                sent_param = None

        queryset = Email.objects.order_by('-count').all()

        if sent_param is not None:
            filtered_queryset = []
            for q in queryset:
                if q.sent == sent_param:
                    filtered_queryset.append(q)
            return filtered_queryset

        # print("queryset")
        # print(vars(queryset))
        return queryset


class LatestRecordViewSet(viewsets.ModelViewSet):
    serializer_class = LatestRecordSerializer
    queryset = LatestRecord.objects.all()

    def get_queryset(self):
        # Get the value of 'sent' parameter from the request query parameters
        sent_param = self.request.query_params.get('sent')
        if sent_param is not None:
            # Convert to lowercase for case-insensitive comparison
            sent_param = sent_param.lower()

            if sent_param == 'true':
                sent_param = True
            elif sent_param == 'false':
                sent_param = False
            else:
                sent_param = None

        queryset = LatestRecord.objects.order_by('-count').all()

        if sent_param is not None:
            filtered_queryset = []
            for q in queryset:
                if q.sent == sent_param:
                    filtered_queryset.append(q)
            return filtered_queryset

        return queryset


class FunderViewSet(viewsets.ModelViewSet):
    serializer_class = FunderSerializer
    queryset = Funder.objects.all()


class PDdfsViewSet(viewsets.ModelViewSet):
    serializer_class = PdfFileSerializer
    queryset = PdfFile.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def pdf_view(self, request, folder, url):
        pdf_file = PdfFile(file=f"pdf_files/{folder}/{url}")
        context = {
            'pdf_url': pdf_file.file,
        }
        # return render(request, 'pdf_viewer.html', context)

        with open(pdf_file.file.path, 'rb') as pdf:
            response = HttpResponse(pdf.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline;filename=mypdf.pdf'
            return response

    def create(self, request, *args, **kwargs):
        if not 'pdf_type' in request.data:
            return Response({"message": "pdf_type is missing"}, status=status.HTTP_400_BAD_REQUEST)
        if not 'application_id' in request.data:
            return Response({"message": "application_id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        if not 'pdf_file' in request.data:
            return Response({"message": "pdf_file is missing"}, status=status.HTTP_400_BAD_REQUEST)

        pdf_type = request.data['pdf_type']
        application_id = request.data['application_id']
        # If the code reaches this point, it means the PdfFile object exists
        # You can use 'check_if_pdf_file_exist' variable here for further processing if needed.
        try:
            check_if_pdf_file_exist = get_object_or_404(
                PdfFile, application_id=application_id, pdf_type=pdf_type)
            return Response({"message": f"{pdf_type} Already exist."}, status=status.HTTP_400_BAD_REQUEST)
        except Http404:
            # If the PdfFile object does not exist, this block will be executed
            # Handle the case where the PdfFile does not exist (e.g., raise an error, return an HTTP response, etc.)
            pass
            
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
            application=application,
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
        pdfFile.save()

        return Response(status=status.HTTP_201_CREATED)


# this route only updates pdf data
@api_view(['PUT'])
def update_pdf_data(request, id):
    try:
        pdf_file = PdfFile.objects.get(id=id)
    except PdfFile.DoesNotExist:
        return Response({"message": "PDF file not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = PdfFileSerializer(pdf_file, data=request.data, partial=True)
    # print(serializer.is_valid())
    if serializer.is_valid():
        serializer.save()
        # try:
        # except Exception as e:
        #     return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_file(request, application_id, pdf_type):
    pdf_file = get_object_or_404(
        PdfFile, application_id=application_id, pdf_type=pdf_type)
    response = HttpResponse(pdf_file.file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_file.file.name}"'
    return response


def get_score(request, application_id):
    score = random.randint(100, 999)
    response_data = {}
    response_data['score'] = score
    application = get_object_or_404(Application, application_id=application_id)
    application.credit_score = score
    serializer = ApplicationSerializer(
        application, data={"credit_score": score}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)
    return JsonResponse({"message": "application not found!", "error": serializer.error}, safe=False, status=status.HTTP_404_NOT_FOUND)


def get_submitted_applications(request, application_id):
    submitted_applications = SubmittedApplication.objects.filter(
        application_id=application_id)

    serialized_application = SubmittedApplicationSerializer(
        submitted_applications, many=True)

    return JsonResponse(serialized_application.data, safe=False, status=status.HTTP_200_OK)


def generate_random_string(length=6):
    """Generate a random alphanumeric string of specified length."""
    characters = string.ascii_letters + string.digits
    r = ''.join(random.choice(characters) for _ in range(length))
    return r


# class AppPagination(PageNumberPagination):
# class AppPagination():
#     page_size = 1000  # Number of objects to be displayed per page
#     # Name of the query parameter for specifying the page size
#     page_size_query_param = 'q'


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.order_by('-count').all()
    serializer_class = ApplicationSerializer
    # pagination_class = AppPagination

    def create(self, request, *args, **kwargs):
        last_application = Application.objects.order_by(
            'count').last()
        if last_application is not None:
            last_count = last_application.count
            # print(last_count)
        else:
            last_count = 0
        data = request.data
        data['count'] = last_count+1
        serializer = ApplicationSerializer(data=request.data)
        # print(serializer.is_valid())
        if serializer.is_valid():
            application = Application(**serializer.validated_data)
            application_id = application.application_id
            application.save()

            response_data = serializer.data
            response_data['application_id'] = application_id
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            try:
                self.perform_update(serializer)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmittedApplicationViewSet(viewsets.ModelViewSet):
    queryset = SubmittedApplication.objects.order_by('-date_submitted').all()
    serializer_class = SubmittedApplicationSerializer
    # pagination_class = AppPagination

    def create(self, request, *args, **kwargs):
        serializer = SubmittedApplicationSerializer(data=request.data)
        # print(serializer.is_valid())
        if serializer.is_valid():
            if 'funder_names' not in request.data:
                return Response({"message": "funder not selected"}, status=status.HTTP_400_BAD_REQUEST)

            funders = request.data['funder_names']
            response_data = {'data': {}, 'error': [], 'success': [], 'failed': []}

            for f in funders:
                try:
                    funder = Funder.objects.filter(name=f['name']).first()
                    if not funder:
                        response_data['error'].append(
                            {'funder_name': f['name'], 'message': 'funder not found'})
                        response_data['failed'].append(f['name'])
                        continue

                    application = Application.objects.filter(
                        application_id=request.data['application_id']).first()
                    submittedApplication = SubmittedApplication(
                        **serializer.validated_data)
                    submittedApplication_id = submittedApplication.submittedApplication_id
                    submittedApplication.application = application
                    submittedApplication.funder = funder
                    total_count = SubmittedApplication.objects.count()
                    submittedApplication.count = total_count+1
                    submittedApplication.save()
                    
                    response_data['success'].append(f['name'])
                except:
                    response_data['failed'].append(f['name'])

            response_data['data'] = serializer.data
            # response_data['submittedApplication_id'] = submittedApplication_id
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        # serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            try:
                self.perform_update(serializer)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_application_stats(status_substring):
    all_apps = SubmittedApplication.objects.filter(
        status__icontains=status_substring)
    app_count = all_apps.count()
    app_sum = all_apps.aggregate(Sum('advanced_price'))[
        'advanced_price__sum'] or 0
    return {'count': app_count, 'sum': app_sum}


def get_starts(request):
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
            (commission_price_from_all_approved_apps_sum*100)/app_sum, 2)
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
