# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, parsers, generics, views
# from requests import Response
from rest_framework import status, exceptions
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .models import *
from .serializers import *
import base64
import tempfile
import PyPDF2
from django.views.decorators.csrf import csrf_exempt
import jwt
import datetime


class RegisterView(views.APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        payload = {
            'id': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        #    .decode('utf-8')
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)

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
            raise exceptions.AuthenticationFailed('User not found!')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Password incorrect')

        payload = {
            'id': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')
        # .decode('utf-8')
        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=True)
        response.data = {"message": 'success'}
        return response

        # return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetAuthUserView(views.APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise exceptions.AuthenticationFailed("Unauthenticated")

        try:
            payload = jwt.decode(token, 'secret', algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            # raise exceptions.AuthenticationFailed('Unauthenticated!')
            return Response({"message": "Unauthenticated!"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.exceptions.InvalidSignatureError:
            # raise exceptions.AuthenticationFailed('Invalid signature!')
            return Response({"message": "Invalid signature!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except jwt.exceptions.ExpiredSignatureError:
            # raise exceptions.AuthenticationFailed('Signature has expired!')
            return Response({"message": "Signature has expired!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except jwt.exceptions.DecodeError:
            # raise exceptions.AuthenticationFailed('Invalid token!')
            return Response({"message": "Invalid token!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            # raise exceptions.AuthenticationFailed('Could not decode token!')
            return Response({"message": "Could not decode token!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            user = CustomUser.objects.filter(email = 'cent@gmail.com').first()
            serializer = UserSerializer(user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except: 
            return Response({"error", "Unsuccessful!"}, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response



def get_application_pdfs(request, application_id):
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
    # print(pdf_data)

    return JsonResponse({'pdfs': pdf_data})


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    queryset = Status.objects.all()


class PDdfsViewSet(viewsets.ModelViewSet):
    serializer_class = PdfFileSerializer
    queryset = PdfFile.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def create(self, request, *args, **kwargs):
        # print(request.data)
        pdf_type = request.data['pdf_type']
        application_id = request.data['application_id']

        business_name = request.data['business_name']
        bank_name = request.data['bank_name']
        begin_bal_amount = request.data['begin_bal_amount']
        begin_bal_date = request.data['begin_bal_date']
        ending_bal_amount = request.data['ending_bal_amount']
        ending_bal_date = request.data['ending_bal_date']
        total_deposit = request.data['total_deposit']

        pdf_file = request.data['pdf_file']

        # print(pdf_file)

        pdfFile = PdfFile.objects.create(
            file=pdf_file,
            pdf_type=pdf_type,
            business_name={business_name},
            bank_name={bank_name},
            begin_bal_amount={begin_bal_amount},
            begin_bal_date={begin_bal_date},
            ending_bal_amount={ending_bal_amount},
            ending_bal_date={ending_bal_date},
            total_deposit={total_deposit}
        )
        pdfFile.save()

        application = Application.objects.get(
            application_id=application_id)
        pdfFile.application_id = application
        pdfFile.save()
        # print(pdfFile)

        return Response(status=status.HTTP_201_CREATED)

        # pdf_file = request.FILES.get('pdf_file')
        # title = request['title']
        # application_id = request['application_id']
        # beginning_balance_amount = request['beginning_balance_amount']

        # applicationPDFs = ApplicationPDFs.objects.create(
        #     file=pdf_file,
        #     pdf_type=title,
        #     beginning_balance_amount=beginning_balance_amount
        # )
        # applicationPDFs.application = Application.objects.get(
        #     application_id=application_id)
        # applicationPDFs.save()

        # if applicationPDFs:
        #     return Response(serializer.data, application_id=application.application_id, status=status.HTTP_201_CREATED)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #     return Response(serializer.data, application_id=application.application_id, status=status.HTTP_201_CREATED)

        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = MovieSerializer(data=request.data)

        if serializer.is_valid():
            # Save the application object
            movie = serializer.save()
            # print(movie)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    # parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = ApplicationSerializer(data=request.data)
        # print(serializer)
        print(serializer.is_valid())

        if serializer.is_valid():
            application = Application(**serializer.validated_data)
            # application = serializer.save()
            print("application: ")
            print(application)

            application_id = application.application_id
            print("application_id: ")
            print(application_id)

            application.status = Status.objects.get(name="Submitted")
            application.save()

            # print(application)
            # print(application.pk)
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
