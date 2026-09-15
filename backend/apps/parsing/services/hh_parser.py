from scrapling.fetchers import Fetcher
from apps.tracker.models import Vacancy

def search_vacancies(url: str, query: str, page: int = 0) -> list[dict]:
    params = {
        'text': query,
        'page': page,
    }


    page_obj = Fetcher.get(url, params=params, impersonate='chrome')
    script_tag = page_obj.css('template#HH-Lux-InitialState').first

    data = script_tag.json()
    vacancies = data.get('vacancySearchResult', {}).get('vacancies')

    return [extract_vacancy_data(vac) for vac in vacancies]


def extract_vacancy_data(vacancy: dict) -> dict:
    return {
        'id': vacancy.get('vacancyId'),
        'title': vacancy.get('name'),
        'company': (vacancy.get('company') or {}).get('name') or '',
        'url': vacancy.get('links', {}).get('desktop'),
        'location': vacancy.get('area', {}).get('name'),
        # 'salary': vacancy.get(''),
        'experience': vacancy.get('workExperience'),
        # 'schedule': vacancy.get(''),
        'employment': vacancy.get('employment', {}).get('@type'),
        'source': 'hh.ru',
    }

def save_vacancy(vacancy_data: dict) -> Vacancy:
    vacancy, _ = Vacancy.objects.get_or_create(
        url=vacancy_data.get('url'),
        defaults={
            'title': vacancy_data.get('title'),
            'company': vacancy_data.get('company'),
            'location': vacancy_data.get('location'),
            'experience': vacancy_data.get('experience'),
            'description': vacancy_data.get('description'),
            'employment': vacancy_data.get('employment'),
            'source': vacancy_data.get('source'),
        })
    return vacancy