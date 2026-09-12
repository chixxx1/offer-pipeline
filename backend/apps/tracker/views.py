# from django.shortcuts import render
from rest_framework import viewsets
from .models import Vacancy, Application
from .serializers import VacancySerializer, ApplicationSerializer

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer