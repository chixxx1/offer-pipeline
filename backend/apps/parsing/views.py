from rest_framework.views import APIView
from rest_framework.response import Response
from apps.parsing.services.hh_parser import search_vacancies, save_vacancy, fetch_vacancy_description
from apps.tracker.serializers import VacancySerializer
from apps.tracker.models import Vacancy


class VacanciesSearchView(APIView):
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({}, status=400)

        vacancies_data = search_vacancies('https://hh.ru/search/vacancy/', query)

        saved_vacancies = []
        for vacancy_data in vacancies_data:
            saved_vacancies.append(save_vacancy(vacancy_data))

        serializer = VacancySerializer(saved_vacancies, many=True)
        return Response(serializer.data)

class VacancyDescriptionView(APIView):
    def get(self, request, vacancy_id):
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({'error': 'Вакансия не найдена'}, status=404)

        if not vacancy.description:
            vacancy.description = fetch_vacancy_description(vacancy.url)
            vacancy.save(update_fields=['description'])

        return Response({'description': vacancy.description})