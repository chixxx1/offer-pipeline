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

def fetch_vacancy_full_description(url: str) -> str:
    page_obj = Fetcher.get(url, impersonate='chrome')
    desc_block = page_obj.css('[data-qa="vacancy-description"]').first
    if not desc_block:
        return ''
    return desc_block.html_content



def extract_vacancy_data(vacancy: dict) -> dict:
    work_formats_list = (vacancy.get('workFormats') or [{}])[0].get('workFormatsElement', [])
    salary = extract_salary(vacancy.get('compensation') or {})

    return {
        'id': vacancy.get('vacancyId'),
        'title': vacancy.get('name'),
        'company': (vacancy.get('company') or {}).get('name') or '',
        'url': vacancy.get('links', {}).get('desktop'),
        'location': vacancy.get('area', {}).get('name'),
        'experience': vacancy.get('workExperience'),
        'employment': vacancy.get('employment', {}).get('@type'),
        'work_format': ', '.join(work_formats_list) if work_formats_list else '',
        'salary_from': salary['salary_from'],
        'salary_to': salary['salary_to'],
        'source': 'hh.ru',
    }

def fetch_vacancy_description(url: str) -> str:
    page_obj = Fetcher.get(url, impersonate='chrome')
    meta_teg = page_obj.css('meta[name="description"]').first
    
    if not meta_teg:
        return ''

    return meta_teg.attrib.get('content', '')

def extract_salary(compensation: dict):
    if not compensation or "noCompensation" in compensation:
        return {
            'salary_from': None,
            'salary_to': None,
            'salary_currency': None,
            'salary_gross': None,
        } 

    return {   
        'salary_from': compensation.get('from'),
        'salary_to': compensation.get('to'),
        'salary_currency': compensation.get('currencyCode'),
        'salary_gross': compensation.get('gross'),
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
            'work_format': vacancy_data.get('work_format'),
            'salary_from': vacancy_data.get('salary_from'),
            'salary_to': vacancy_data.get('salary_to'),
            'source': vacancy_data.get('source'),
        })
    return vacancy