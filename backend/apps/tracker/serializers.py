from rest_framework import serializers
from .models import Vacancy, Application, VacancyRecommendation
from django.contrib.auth.models import User
from apps.users.serializers import SkillSerializer


class VacancySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    match = serializers.SerializerMethodField()

    class Meta:
        model = Vacancy
        fields = [
            'id', 'title', 'company', 'url', 'description', 'source',
            'salary_from', 'salary_to', 'created_at', 'published_at',
            'skills', 'match',
        ]

    def get_match(self, obj) -> int | None:
        """Расчётное поле мэтчинга для текущего пользователя (из контекста)."""
        profile = self.context.get('profile')
        variant = self.context.get('variant')
        if profile is None:
            return None
        from apps.tracker.services.matching import calculate_vacancy_match
        match = calculate_vacancy_match(obj, profile, variant=variant)
        return match['score']


class ApplicationSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)
    vacancy_id = serializers.PrimaryKeyRelatedField(
        queryset=Vacancy.objects.all(), source='vacancy', write_only=True
    )

    class Meta:
        model = Application
        fields = ['id', 'vacancy', 'vacancy_id',  'notes', 'status', 'created_at', 'updated_at', 'applied_at']


class VacancyRecommendationSerializer(serializers.ModelSerializer):
    vacancy = VacancySerializer(read_only=True)

    class Meta:
        model = VacancyRecommendation
        fields = [
            'id', 'vacancy', 'variant', 'score', 'matched_skills',
            'missing_skills', 'reasons', 'is_new', 'is_dismissed',
            'notified_in_tg', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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