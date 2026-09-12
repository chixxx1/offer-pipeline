from rest_framework import serializers
from .models import Vacancy, Application

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