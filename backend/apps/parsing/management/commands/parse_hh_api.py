import requests
from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **cmd_options):

        params = {
            'text': 'python developer',
            'area': '1',
        }

        header = {
            'User-Agent': 'OfferPipeline/1.0 (denakos33@gmail.com)'
        }

        res = requests.get('https://api.hh.ru/vacancies', params=params, headers=header, timeout=5)
        res.raise_for_status()

        data = res.json()

        self.stdout.write(str(data))