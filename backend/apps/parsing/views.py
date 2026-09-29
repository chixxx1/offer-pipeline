from rest_framework.views import APIView
from rest_framework.response import Response
from apps.parsing.services.hh_parser import search_vacancies, save_vacancy_batch, fetch_vacancy_full_description
from apps.tracker.serializers import VacancySerializer
from apps.tracker.models import Vacancy


class VacanciesSearchView(APIView):
    def post(self, request):
        query = request.data.get('query')

        experience = request.data.get('experience')
        work_format = request.data.get('work_format')
        salary_from = request.data.get('salary_from')
        work_schedule_by_days = request.data.get('work_schedule_by_days')
        employment_form = request.data.get('employment_form')

        if not query:
            return Response({}, status=400)

        vacancies_data = search_vacancies(
            'https://hh.ru/search/vacancy/', 
            query,
            experience=experience,
            work_format=work_format,
            salary_from=salary_from,
            work_schedule_by_days=work_schedule_by_days,
            employment_form=employment_form,
            )
        saved_vacancies = save_vacancy_batch(vacancies_data)

        serializer = VacancySerializer(saved_vacancies, many=True)
        return Response(serializer.data)

class VacancyFullDescriptionView(APIView):
    def get(self, request, vacancy_id):
        try:
            vacancy = Vacancy.objects.get(id=vacancy_id)
        except Vacancy.DoesNotExist:
            return Response({'error': 'Вакансия не найдена'}, status=404)

        full_description = fetch_vacancy_full_description(vacancy.url)
        return Response({'full_description': full_description})