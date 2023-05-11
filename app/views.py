from django.shortcuts import get_object_or_404
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
            return Response({"message": "User not found"})

        if not user.check_password(password):
            return Response({"message": "Password incorrect"})

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
            # raise exceptions.AuthenticationFailed("Unauthenticated")
            return Response({"message": "Unauthenticated!"})

        try:
            payload = jwt.decode(token, 'secret', algorithms=["HS256"])
        except jwt.exceptions.DecodeError:
            return Response({"message": "Unauthenticated!"})
        except jwt.exceptions.InvalidSignatureError:
            return Response({"message": "Invalid signature!"})
        except jwt.exceptions.ExpiredSignatureError:
            return Response({"message": "Signature has expired!"})
        except jwt.exceptions.DecodeError:
            return Response({"message": "Invalid token!"})
        except:
            return Response({"message": "Could not decode token!"})

        try:
            user = CustomUser.objects.filter(email=payload['id']).first()
            serializer = UserSerializer(user)
            response_data = serializer.data
            response_data['message'] = 'success'
            return Response(response_data, status=status.HTTP_200_OK)
        except:
            return Response({"error", "Unsuccessful!"})


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


class FunderViewSet(viewsets.ModelViewSet):
    serializer_class = FunderSerializer
    queryset = Funder.objects.all()


class PDdfsViewSet(viewsets.ModelViewSet):
    serializer_class = PdfFileSerializer
    queryset = PdfFile.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def create(self, request, *args, **kwargs):
        # print(request.data)
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
            business_name={business_name},
            bank_name={bank_name},
            begin_bal_amount={begin_bal_amount},
            begin_bal_date={begin_bal_date},
            ending_bal_amount={ending_bal_amount},
            ending_bal_date={ending_bal_date},
            total_deposit={total_deposit}
        )
        # pdfFile.save()
        pdfFile.application_id = application
        pdfFile.save()
        # print(pdfFile)

        return Response(status=status.HTTP_201_CREATED)

        # print(application)

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


def get_file(request, application_id, pdf_type):
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
    # try:
    #     # submitted_application = get_object_or_404(
    #     #     SubmittedApplication, application_id=application_id)

    # except SubmittedApplication.DoesNotExist:
    #     return Response({'error': 'Submitted application not found.'}, status=status.HTTP_404_NOT_FOUND)

    submitted_applications = SubmittedApplication.objects.filter(
        application_id=application_id)

    serialized_application = SubmittedApplicationSerializer(
        submitted_applications, many=True)

    return JsonResponse(serialized_application.data, safe=False, status=status.HTTP_200_OK)


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
        print("request.data: ")
        print(request.data)
        serializer = ApplicationSerializer(data=request.data)
        # print(serializer)
        print(serializer.is_valid())

        if serializer.is_valid():
            application = Application(**serializer.validated_data)
            application_id = application.application_id
            application.save()

            response_data = serializer.data
            print("response_data: ")
            print(response_data)
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
    # parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        # print(request.data)
        serializer = SubmittedApplicationSerializer(data=request.data)
        # print(serializer)
        print(serializer.is_valid())

        if serializer.is_valid():
            if not 'funder_names' in request.data:
                return Response({"message": "funder not selected"}, status=status.HTTP_201_CREATED)
            funder_names = request.data['funder_names']
            print(funder_names)
            for funder_name in funder_names:
                funder = Funder.objects.filter(
                    name=funder_name['name']).first()
                if funder:
                    submittedApplication = SubmittedApplication(
                        **serializer.validated_data)
                    submittedApplication.funder = funder
                    submittedApplication.save()
                    submittedApplication_id = submittedApplication.application_id

                    response_data = serializer.data
                    response_data['submittedApplication_id'] = submittedApplication_id

                    return Response(response_data, status=status.HTTP_201_CREATED)

                return Response({"message": "funder not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(status=status.HTTP_201_CREATED)
