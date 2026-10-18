from django.core.files.uploadedfile import UploadedFile
from rest_framework import serializers

from .models import (
    Education,
    Profile,
    ProfileVariant,
    ResumeFile,
    Skill,
    WorkExperience,
)


class SkillNamesField(serializers.Field):

    def to_internal_value(self, data):
        if not isinstance(data, list):
            raise serializers.ValidationError('Ожидается список названий навыков.')
        names = []
        for raw in data:
            if not isinstance(raw, str):
                raise serializers.ValidationError('Название навыка должно быть строкой.')
            name = Skill.normalize_name(raw)
            if not name:
                raise serializers.ValidationError('Название навыка не может быть пустым.')
            if name not in names:
                names.append(name)
        return names

    def to_representation(self, value):
        return [skill.name for skill in value.all()]


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = ['id', 'company', 'position', 'start_date', 'end_date', 'is_current', 'description']
        read_only_fields = ['id']

    def validate(self, attrs):
        end_date = attrs.get('end_date', getattr(self.instance, 'end_date', None))
        start_date = attrs.get('start_date', getattr(self.instance, 'start_date', None))
        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': 'Дата окончания не может быть раньше даты начала.'})
        if attrs.get('is_current'):
            attrs['end_date'] = None
        return attrs


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'institution', 'degree', 'field_of_study', 'start_year', 'end_year']
        read_only_fields = ['id']

    def validate(self, attrs):
        end_year = attrs.get('end_year', getattr(self.instance, 'end_year', None))
        start_year = attrs.get('start_year', getattr(self.instance, 'start_year', None))
        if end_year is not None and start_year and end_year < start_year:
            raise serializers.ValidationError({'end_year': 'Год окончания не может быть раньше года начала.'})
        return attrs


class ProfileVariantSerializer(serializers.ModelSerializer):
    skills = SkillNamesField(required=False)
    experience_ids = serializers.PrimaryKeyRelatedField(
        source='experiences',
        queryset=WorkExperience.objects.none(),
        many=True,
        required=False,
    )

    class Meta:
        model = ProfileVariant
        fields = ['id', 'title', 'about', 'skills', 'experience_ids']
        read_only_fields = ['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None and request.user.is_authenticated:
            self.fields['experience_ids'].child_relation.queryset = WorkExperience.objects.filter(
                profile__user=request.user,
            )

    def create(self, validated_data):
        skills = validated_data.pop('skills', [])
        experiences = validated_data.pop('experiences', [])
        instance = super().create(validated_data)
        instance.skills.set([Skill.get_or_create_normalized(name) for name in skills])
        instance.experiences.set(experiences)
        return instance

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        experiences = validated_data.pop('experiences', None)
        instance = super().update(instance, validated_data)
        if skills is not None:
            instance.skills.set([Skill.get_or_create_normalized(name) for name in skills])
        if experiences is not None:
            instance.experiences.set(experiences)
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    skills = SkillNamesField(required=False)
    variants = ProfileVariantSerializer(many=True, read_only=True)
    experiences = WorkExperienceSerializer(many=True, read_only=True)
    education = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            'id', 'about', 'city', 'desired_salary', 'work_format',
            'github_url', 'linkedin_url', 'telegram', 'contact_email',
            'skills', 'variants', 'experiences', 'education',
        ]
        read_only_fields = ['id']

    def update(self, instance, validated_data):
        skills = validated_data.pop('skills', None)
        instance = super().update(instance, validated_data)
        if skills is not None:
            skill_objects = [Skill.get_or_create_normalized(name) for name in skills]
            instance.skills.set(skill_objects)
        return instance


class ResumeFileSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)

    class Meta:
        model = ResumeFile
        fields = ['id', 'file', 'original_name', 'variant', 'uploaded_at']
        read_only_fields = ['id', 'original_name', 'uploaded_at']

    def validate_file(self, value: UploadedFile):
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError('Размер файла не должен превышать 10 МБ.')
        extension = value.name.lower().rsplit('.', 1)[-1] if '.' in value.name else ''
        if extension not in ('pdf', 'docx'):
            raise serializers.ValidationError('Разрешены только файлы .pdf и .docx.')
        return value

    def validate_variant(self, value):
        if value is not None and value.profile.user != self.context['request'].user:
            raise serializers.ValidationError('Вариант профиля не найден.')
        return value

    def create(self, validated_data):
        validated_data['original_name'] = self.initial_data.get('original_name') or self.context['request'].FILES['file'].name
        return super().create(validated_data)
