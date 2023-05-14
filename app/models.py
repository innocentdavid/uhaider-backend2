from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
import random
import string


class CustomUser(AbstractUser):
    name = models.CharField(max_length=255, default='')
    email = models.CharField(max_length=255, primary_key=True, unique=True)
    password = models.CharField(max_length=255)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


def generate_random_string(length=6):
    """Generate a random alphanumeric string of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


class Funder(models.Model):
    email = models.EmailField(
        max_length=255, default="", blank=False)
    name = models.CharField(
        max_length=255, default="", blank=False)
    phone = models.CharField(
        max_length=255, default="", blank=True)

    def __str__(self):
        return self.name


class Application(models.Model):
    count = models.IntegerField(default=0)
    application_id = models.CharField(
        max_length=250, primary_key=True, unique=True, default=generate_random_string)
    date_submitted = models.CharField(
        max_length=255, default="", blank=True)
    # status = models.ForeignKey(
    #     Status, on_delete=models.PROTECT, related_name='applications', blank=True)
    status = models.CharField(
        max_length=255, default="Created", blank=True)
    status_description = models.CharField(
        max_length=255, default="Created", blank=True)
    status_date = models.CharField(
        max_length=255, default="", blank=True)

    owners = models.CharField(
        max_length=255, default="", blank=True)
    business_name_match_flag = models.CharField(
        max_length=255, default="", blank=True)
    credit_score = models.CharField(
        max_length=255, default="", blank=True)

    name_of_business = models.CharField(
        max_length=255, default="", blank=True)
    legal_business_name = models.CharField(
        max_length=255, default="", blank=True)
    dba = models.CharField(max_length=255, default="", blank=True)
    address = models.CharField(
        max_length=255, default="", blank=True)
    suite = models.CharField(max_length=255, default="", blank=True)
    city = models.CharField(max_length=255, default="", blank=True)
    state = models.CharField(max_length=255, default="", blank=True)
    zip = models.CharField(max_length=255, default="", blank=True)
    phone = models.CharField(max_length=255, default="", blank=True)
    legal_entry = models.CharField(
        max_length=255, default="", blank=True)
    state_inc = models.CharField(
        max_length=255, default="", blank=True)
    federal_tax_id = models.CharField(
        max_length=255, default="", blank=True)
    date_business_started = models.CharField(
        max_length=255, default="", blank=True)
    years_at_location = models.CharField(
        max_length=255, default="", blank=True)
    number_of_locations = models.CharField(
        max_length=255, default="", blank=True)
    length_of_ownership = models.CharField(
        max_length=255, default="", blank=True)
    state_of_inc = models.CharField(
        max_length=255, default="", blank=True)
    legal_entity = models.CharField(
        max_length=255, default="", blank=True)
    mobile = models.CharField(
        max_length=255, default="", blank=True)
    email = models.CharField(max_length=255, default="", blank=True)

    owner_first_name = models.CharField(
        max_length=255, default="", blank=True)
    owner_last_name = models.CharField(
        max_length=255, default="", blank=True)
    owner_home_address = models.CharField(
        max_length=255, default="", blank=True)
    owner_city = models.CharField(
        max_length=255, default="", blank=True)
    owner_state = models.CharField(
        max_length=255, default="", blank=True)
    owner_zip = models.CharField(
        max_length=255, default="", blank=True)
    owner_ssn = models.CharField(
        max_length=255, default="", blank=True)
    owner_percentage_of_ownership = models.CharField(
        max_length=255, default="", blank=True)
    owner_dob = models.CharField(
        max_length=255, default="", blank=True)
    owner_phone = models.CharField(
        max_length=255, default="", blank=True)

    gross_monthly_sales = models.CharField(
        max_length=255, default="", blank=True)
    type_of_product_sold = models.CharField(
        max_length=255, default="", blank=True)
    has_open_cash_advances = models.CharField(
        max_length=255, default="", blank=True)
    has_used_cash_advance_plan_before = models.CharField(
        max_length=255, default="", blank=True)
    using_money_for = models.CharField(
        max_length=255, default="", blank=True)
    description_of_business = models.CharField(
        max_length=255, default="", blank=True)

    advanced_price = models.IntegerField(default=0)
    commission_price = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    factor = models.IntegerField(default=0)
    total_fee = models.IntegerField(default=0)
    payback = models.IntegerField(default=0)
    term = models.CharField(
        max_length=255, default="", blank=True)
    frequency = models.IntegerField(default=0)
    payment = models.IntegerField(default=0)
    net_funding_amount = models.IntegerField(default=0)

    # def save(self, *args, **kwargs):
    #     self.count += 1
    #     super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # If this is a new instance, increment the count field
    #     if not self.pk:
    #         self.count = MyModel.objects.count() + 1

    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_of_business} - {self.status}"


class SubmittedApplication(models.Model):
    count = models.IntegerField(default=0)
    funder = models.ForeignKey(Funder, on_delete=models.CASCADE, related_name='funder', blank=True, null=True)
    submittedApplication_id = models.CharField(
        max_length=250, primary_key=True, unique=True, default=generate_random_string)
    application_id = models.CharField(
        max_length=250, default='')
    date_submitted = models.CharField(
        max_length=255, default="", blank=True)
    # status = models.ForeignKey(
    #     Status, on_delete=models.PROTECT, related_name='applications', blank=True)
    status = models.CharField(
        max_length=255, default="Created", blank=True)
    status_description = models.CharField(
        max_length=255, default="Created", blank=True)
    status_date = models.CharField(
        max_length=255, default="", blank=True)

    owners = models.CharField(
        max_length=255, default="", blank=True)
    business_name_match_flag = models.CharField(
        max_length=255, default="", blank=True)
    credit_score = models.CharField(
        max_length=255, default="", blank=True)

    name_of_business = models.CharField(
        max_length=255, default="", blank=True)
    legal_business_name = models.CharField(
        max_length=255, default="", blank=True)
    dba = models.CharField(max_length=255, default="", blank=True)
    address = models.CharField(
        max_length=255, default="", blank=True)
    suite = models.CharField(max_length=255, default="", blank=True)
    city = models.CharField(max_length=255, default="", blank=True)
    state = models.CharField(max_length=255, default="", blank=True)
    zip = models.CharField(max_length=255, default="", blank=True)
    phone = models.CharField(max_length=255, default="", blank=True)
    legal_entry = models.CharField(
        max_length=255, default="", blank=True)
    state_inc = models.CharField(
        max_length=255, default="", blank=True)
    federal_tax_id = models.CharField(
        max_length=255, default="", blank=True)
    date_business_started = models.CharField(
        max_length=255, default="", blank=True)
    years_at_location = models.CharField(
        max_length=255, default="", blank=True)
    number_of_locations = models.CharField(
        max_length=255, default="", blank=True)
    length_of_ownership = models.CharField(
        max_length=255, default="", blank=True)
    state_of_inc = models.CharField(
        max_length=255, default="", blank=True)
    legal_entity = models.CharField(
        max_length=255, default="", blank=True)
    mobile = models.CharField(
        max_length=255, default="", blank=True)
    email = models.CharField(max_length=255, default="", blank=True)

    owner_first_name = models.CharField(
        max_length=255, default="", blank=True)
    owner_last_name = models.CharField(
        max_length=255, default="", blank=True)
    owner_home_address = models.CharField(
        max_length=255, default="", blank=True)
    owner_city = models.CharField(
        max_length=255, default="", blank=True)
    owner_state = models.CharField(
        max_length=255, default="", blank=True)
    owner_zip = models.CharField(
        max_length=255, default="", blank=True)
    owner_ssn = models.CharField(
        max_length=255, default="", blank=True)
    owner_percentage_of_ownership = models.CharField(
        max_length=255, default="", blank=True)
    owner_dob = models.CharField(
        max_length=255, default="", blank=True)
    owner_phone = models.CharField(
        max_length=255, default="", blank=True)

    gross_monthly_sales = models.CharField(
        max_length=255, default="", blank=True)
    type_of_product_sold = models.CharField(
        max_length=255, default="", blank=True)
    has_open_cash_advances = models.CharField(
        max_length=255, default="", blank=True)
    has_used_cash_advance_plan_before = models.CharField(
        max_length=255, default="", blank=True)
    using_money_for = models.CharField(
        max_length=255, default="", blank=True)
    description_of_business = models.CharField(
        max_length=255, default="", blank=True)

    advanced_price = models.IntegerField(default=0)
    commission_price = models.IntegerField(default=0)
    percentage = models.IntegerField(default=0)
    factor = models.IntegerField(default=0)
    total_fee = models.IntegerField(default=0)
    payback = models.IntegerField(default=0)
    term = models.CharField(
        max_length=255, default="", blank=True)
    frequency = models.IntegerField(default=0)
    payment = models.IntegerField(default=0)
    net_funding_amount = models.IntegerField(default=0)

    # def save(self, *args, **kwargs):
    #     self.count += 1
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name_of_business} - {self.status}"


class PdfFile(models.Model):
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="pdfFiles")
    file = models.FileField(upload_to='pdf_files/')
    # file = models.BinaryField()
    pdf_type = models.CharField(
        max_length=255, default="", blank=True)

    business_name = models.CharField(
        max_length=255, default="", blank=True)
    bank_name = models.CharField(
        max_length=255, default="", blank=True)
    begin_bal_date = models.CharField(
        max_length=255, default="", blank=True)
    begin_bal_amount = models.CharField(
        max_length=255, default="", blank=True)
    total_deposit = models.CharField(
        max_length=255, default="", blank=True)
    ending_bal_date = models.CharField(
        max_length=255, default="", blank=True)
    ending_bal_amount = models.CharField(
        max_length=255, default="", blank=True)

    def __str__(self):
        return f'{self.business_name} ({self.file.name})'
