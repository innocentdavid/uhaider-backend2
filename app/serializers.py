from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class ApplicationPDFsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationPDFs
        fields = '__all__'


class PdfFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfFile
        fields = '__all__'
        

class ApplicationSerializer(serializers.ModelSerializer):
    # status_description = serializers.CharField(source='status.description', read_only=True)

    class Meta:
        model = Application
        fields = "__all__"
        # depth = 1


class ApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'name_of_business',
            'status_date',
            'advanced_price',
            'commission_price',
            'percentage',
            'factor',
            'total_fee',
            'payback',
            'term',
            'frequency',
            'payment',
            'net_funding_amount',
        ]
