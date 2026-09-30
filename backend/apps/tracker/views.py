# from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Vacancy, Application
from .serializers import VacancySerializer, ApplicationSerializer

class VacancyViewSet(viewsets.ModelViewSet):
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer

class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def create(self, request, *args, **kwargs):
        vacancy_id = request.data.get('vacancy_id')
        existing = Application.objects.filter(vacancy_id=vacancy_id).first()

        if existing:
            serializer = self.get_serializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)