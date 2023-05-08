from rest_framework import serializers
from rest_framework.parsers import MultiPartParser
from rest_framework.viewsets import ModelViewSet
from .models import *
from rest_framework import serializers
from .models import CustomUser




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user


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
    class Meta:
        model = Application
        fields = "__all__"
