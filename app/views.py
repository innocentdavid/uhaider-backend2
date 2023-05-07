# from django.shortcuts import render
from rest_framework import viewsets, parsers, generics
# from requests import Response
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *
import base64


class StatusViewSet(viewsets.ModelViewSet):
    serializer_class = StatusSerializer
    queryset = Status.objects.all()


class PDdfsViewSet(viewsets.ModelViewSet):
    serializer_class = PdfFileSerializer
    queryset = PdfFile.objects.all()
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def create(self, request, *args, **kwargs):
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

            print(application)
            print(application.pk)
            response_data = serializer.data
            response_data['application_id'] = application_id

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
