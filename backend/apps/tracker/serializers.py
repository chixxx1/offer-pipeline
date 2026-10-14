from rest_framework import serializers
from .models import Vacancy, Application
from django.contrib.auth.models import User

class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = ['id', 'title', 'company', 'url', 'description', 'source', 'salary_from', 'salary_to', 'created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(), source='vacancy', write_only=True
    )

    class Meta:
        model = Application
        fields = ['id', 'vacancy', 'vacancy_id',  'notes', 'status', 'created_at', 'updated_at', 'applied_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']