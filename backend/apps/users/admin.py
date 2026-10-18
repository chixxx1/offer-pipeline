from django.contrib import admin

from .models import (
    Education,
    Profile,
    ProfileVariant,
    ResumeFile,
    Skill,
    WorkExperience,
)


class WorkExperienceInline(admin.TabularInline):
    model = WorkExperience
    extra = 0


class EducationInline(admin.TabularInline):
    model = Education
    extra = 0


class ProfileVariantInline(admin.TabularInline):
    model = ProfileVariant
    extra = 0


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    search_fields = ['name']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'city', 'work_format', 'desired_salary']
    list_filter = ['work_format']
    search_fields = ['user__username', 'city']
    inlines = [WorkExperienceInline, EducationInline, ProfileVariantInline]
    filter_horizontal = ['skills']


@admin.register(ResumeFile)
class ResumeFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile', 'variant', 'original_name', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['profile__user__username', 'original_name']
