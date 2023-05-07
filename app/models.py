from django.db import models
from django.utils import timezone

import random
import string


def generate_random_string(length=6):
    """Generate a random alphanumeric string of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class Movie(models.Model):
    movie_id = models.CharField(
        max_length=250, default=generate_random_string)
    name = models.CharField(max_length=250, default="", null=True, blank=True)
    genre = models.CharField(max_length=2550, default="", null=True, blank=True)
    starring = models.CharField(
        max_length=350, default="", null=True, blank=True)
    users_cash_advance = models.CharField(
        max_length=255, default="", null=True, blank=True)

    def __str__(self):
        return self.name


class Status(models.Model):
    name = models.CharField(max_length=255, primary_key=True, default="Submited", null=False, blank=False)
    description = models.CharField(
        max_length=255, default="", null=True, blank=True)

    def __str__(self):
        return self.name


class Application(models.Model):
    application_id = models.CharField(
        max_length=250, primary_key=True, default=generate_random_string)
    date_submitted = models.CharField(
        max_length=255, default="", null=True, blank=True)
    status = models.ForeignKey(
        Status, on_delete=models.PROTECT, related_name='applications', null=True, blank=True)

    name_of_business = models.CharField(
        max_length=255, default="", null=True, blank=True)

    status_date = models.CharField(
        max_length=255, default="", null=True, blank=True)
    legal_business_name = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owners = models.CharField(
        max_length=255, default="", null=True, blank=True)
    users_cash_advance = models.CharField(
        max_length=255, default="", null=True, blank=True)
    have_cash_advance = models.CharField(
        max_length=255, default="", null=True, blank=True)

    dba = models.CharField(max_length=255, default="", null=True, blank=True)
    address = models.CharField(
        max_length=255, default="", null=True, blank=True)
    suite = models.CharField(max_length=255, default="", null=True, blank=True)
    city = models.CharField(max_length=255, default="", null=True, blank=True)
    state = models.CharField(max_length=255, default="", null=True, blank=True)
    zip = models.CharField(max_length=255, default="", null=True, blank=True)
    phone = models.CharField(max_length=255, default="", null=True, blank=True)
    legal_entry = models.CharField(
        max_length=255, default="", null=True, blank=True)
    state_inc = models.CharField(
        max_length=255, default="", null=True, blank=True)
    federal_tax_id = models.CharField(
        max_length=255, default="", null=True, blank=True)
    date_business_started = models.CharField(
        max_length=255, default="", null=True, blank=True)
    mobile = models.CharField(max_length=255, default="", null=True, blank=True)
    email = models.CharField(max_length=255, default="", null=True, blank=True)

    owner_first_name = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_last_name = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_home_address = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_city = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_state = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_zip = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_ssn = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_percentage_of_ownership = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_dob = models.CharField(
        max_length=255, default="", null=True, blank=True)
    owner_phone = models.CharField(
        max_length=255, default="", null=True, blank=True)

    federal_tax_id = models.CharField(
        max_length=255, default="", null=True, blank=True)
    state_of_inc = models.CharField(
        max_length=255, default="", null=True, blank=True)
    legal_entity = models.CharField(
        max_length=255, default="", null=True, blank=True)
    date_business_started = models.CharField(max_length=255, default="", null=True, blank=True)
    gross_monthly_sales = models.CharField(
        max_length=255, default="", null=True, blank=True)
    type_of_product_sold = models.CharField(
        max_length=255, default="", null=True, blank=True)
    has_open_cash_advances = models.CharField(
        max_length=255, default="", null=True, blank=True)
    has_used_cash_advance_plan_before = models.CharField(
        max_length=255, default="", null=True, blank=True)
    using_money_for = models.CharField(
        max_length=255, default="", null=True, blank=True)
    bank_name = models.CharField(
        max_length=255, default="", null=True, blank=True)
    begin_bal_date = models.CharField(
        max_length=255, default="", null=True, blank=True)
    begin_bal_amount = models.CharField(
        max_length=255, default="", null=True, blank=True)
    description_of_business = models.CharField(
        max_length=255, default="", null=True, blank=True)
    length_of_ownership = models.CharField(
        max_length=255, default="", null=True, blank=True)
    years_at_location = models.CharField(
        max_length=255, default="", null=True, blank=True)
    credit_score = models.CharField(
        max_length=255, default="", null=True, blank=True)
    ending_bal_amount = models.CharField(
        max_length=255, default="", null=True, blank=True)
    ending_bal_date = models.CharField(
        max_length=255, default="", null=True, blank=True)
    total_deposit = models.CharField(
        max_length=255, default="", null=True, blank=True)
    business_name_match_flag = models.CharField(
        max_length=255, default="", null=True, blank=True)
    advanced_price = models.CharField(
        max_length=255, default="", null=True, blank=True)
    commission_price = models.CharField(
        max_length=255, default="", null=True, blank=True)

    def __str__(self):
        return f"{self.name_of_business} - {self.status}"


class ApplicationPDFs(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="applicationPDFs")
    file = models.FileField(upload_to='pdf_files/')
    pdf_type = models.CharField(
        max_length=255, default="", null=True, blank=True)

    business_name = models.CharField(
        max_length=255, default="", null=True, blank=True)
    bank_name=models.CharField(
        max_length=255, default="", null=True, blank=True)
    begin_bal_date=models.CharField(
        max_length=255, default="", null=True, blank=True)
    begin_bal_amount=models.CharField(
        max_length=255, default="", null=True, blank=True)
    total_deposit=models.CharField(
        max_length=255, default="", null=True, blank=True)
    ending_bal_date=models.CharField(
        max_length=255, default="", null=True, blank=True)
    ending_bal_amount=models.CharField(
        max_length=255, default="", null=True, blank=True)



    def __str__(self):
        return f'{self.business_name} ({self.file.name})'


class PdfFile(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="pdfFiles")
    file = models.FileField(upload_to='pdf_files/')
    pdf_type = models.CharField(
        max_length=255, default="", null=True, blank=True)

    business_name = models.CharField(
        max_length=255, default="", null=True, blank=True)
    bank_name=models.CharField(
        max_length=255, default="", null=True, blank=True)
    begin_bal_date=models.CharField(
        max_length=255, default="", null=True, blank=True)
    begin_bal_amount=models.CharField(
        max_length=255, default="", null=True, blank=True)
    total_deposit=models.CharField(
        max_length=255, default="", null=True, blank=True)
    ending_bal_date=models.CharField(
        max_length=255, default="", null=True, blank=True)
    ending_bal_amount=models.CharField(
        max_length=255, default="", null=True, blank=True)



    def __str__(self):
        return f'{self.business_name} ({self.file.name})'
