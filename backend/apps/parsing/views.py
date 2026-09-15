from rest_framework.views import APIView
from rest_framework.response import Response
from apps.parsing.services.hh_parser import search_vacancies, save_vacancy
from apps.tracker.serializers import VacancySerializer


class VacanciesSearchView(APIView):
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({}, status=400)

        vacancies_data = search_vacancies('https://hh.ru/search/vacancy/', query)

        saved_vacancies = []
        for vacancy_data in vacancies_data:
            sv_vac = save_vacancy(vacancy_data)
            saved_vacancies.append(sv_vac)

        serializer = VacancySerializer(saved_vacancies, many=True)
        return Response(serializer.data)