from django.core.management import BaseCommand
from apps.parsing.services.hh_parser import search_vacancies, save_vacancy

import json

class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        vacancies_data = search_vacancies(
            'https://hh.ru/search/vacancy/',
            'golang developer'
        )

        # created_count = 0
        for vacancy_data in vacancies_data:
            save_vacancy(vacancy_data)
            # if created:
            #     created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Обработано вакансий {len(vacancies_data)}') # ; добавлено новых {created_count}
        )

