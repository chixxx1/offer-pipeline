from django.contrib import admin
from .models import Vacancy, Application

# добавить опыт для отображения и возможности сортировки по опыту

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'url', 'source', 'salary_from')
    list_filter = ('source',)
    search_fields = ('title', 'company')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('vacancy', 'status', 'created_at', 'applied_at')
    list_filter = ('status',)
    search_fields = ('vacancy__title', 'status')