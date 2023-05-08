# from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import viewsets, parsers, generics
# from requests import Response
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .serializers import *
import base64
import tempfile
import PyPDF2


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
        print(request.data)
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

            print(application)
            print(application.pk)
            response_data = serializer.data
            response_data['application_id'] = application_id

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def update_application(request, application_id):
    try:
        application = Application.objects.get(
            application_id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
            
    status_name = request.data.get('status')
    status_description = request.data.get('status_description')
    if status_name:
        status_obj, created = Status.objects.get_or_create(
            name=status_name, description=status_description)
        application.status = status_obj
        application.save()

    # Update other fields as necessary
    application.name_of_business = request.data.get('name_of_business')
    application.status_date = request.data.get('status_date')
    application.advanced_price = request.data.get('advanced_price')
    application.commission_price = request.data.get('commission_price')
    application.percentage = request.data.get('percentage')
    application.factor = request.data.get('factor')
    application.total_fee = request.data.get('total_fee')
    application.payback = request.data.get('payback')
    application.term = request.data.get('term')
    application.frequency = request.data.get('frequency')
    application.payment = request.data.get('payment')
    application.net_funding_amount = request.data.get('net_funding_amount')


    # Update other fields here

    application.save()


    # return JsonResponse({'success': 'true'})
    return Response({"status": "success"}, status=status.HTTP_200_OK)


class ApplicationUpdateView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationUpdateSerializer

    def post(self, request, application_id):
        try:
            application = Application.objects.get(application_id=application_id)
        except Application.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
            
        status_name = request.data.get('status')
        status_description = request.data.get('status_description')
        if status_name:
            status_obj, created = Status.objects.get_or_create(
                name=status_name, description=status_description)
            application.status = status_obj
            application.save()

        # Update other fields as necessary
        application.name_of_business = request.data.get('name_of_business')
        application.status_date = request.data.get('status_date')
        application.advanced_price = request.data.get('advanced_price')
        application.commission_price = request.data.get('commission_price')
        application.percentage = request.data.get('percentage')
        application.factor = request.data.get('factor')
        application.total_fee = request.data.get('total_fee')
        application.payback = request.data.get('payback')
        application.term = request.data.get('term')
        application.frequency = request.data.get('frequency')
        application.payment = request.data.get('payment')
        application.net_funding_amount = request.data.get('net_funding_amount')


        # Update other fields here

        application.save()

        return Response({"message": "Application updated successfully"})

    # def patch(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.get_serializer(
    #         instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     application = serializer.save()

    #     application.status = Status.objects.get_or_create(
    #         name=request.data.get('status'))
    #     application.save()

    #     return Response(serializer.data)
