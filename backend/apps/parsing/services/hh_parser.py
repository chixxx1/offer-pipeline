from scrapling.fetchers import Fetcher
from apps.tracker.models import Vacancy
from apps.users.models import Skill
from django.utils import dateparse


class CaptchaDetected(Exception):
    """Исключение, которое выбрасывается, когда hh.ru отдаёт страницу с капчей."""


def _raise_if_captcha(page, url: str) -> None:
    """Проверяет ответ hh.ru на наличие капчи и бросает исключение при обнаружении."""
    final_url = str(getattr(page, 'url', '') or '')
    text = ''
    try:
        text = getattr(page, 'text', '') or ''
    except Exception:
        text = ''
    combined = (final_url + ' ' + text).lower()
    if '/account/captcha' in combined or 'captcha' in combined:
        raise CaptchaDetected(
            'hh.ru временно запросил капчу, подождите несколько минут'
        )


def _parse_published_at(raw) -> str | None:
    """Превращает сырую дату публикации hh.ru в aware datetime (ISO-строку)."""
    if not raw:
        return None
    if isinstance(raw, (int, float)):
        from datetime import datetime, timezone
        return datetime.fromtimestamp(raw, tz=timezone.utc).isoformat()
    parsed = dateparse.parse_date(str(raw))
    if parsed:
        from django.utils import timezone as dj_timezone
        if parsed.tzinfo is None:
            parsed = dj_timezone.make_aware(parsed)
        return parsed.isoformat()
    return None


def search_vacancies(
    url: str,
    query: str,
    page: int = 0,
    experience: list[str] | None = None,
    work_format: list[str] | None = None,
    salary_from: int | None = None,
    work_schedule_by_days: list[str] | None = None,
    employment_form: list[str] | None = None,
    order_by: str | None = None,
) -> list[dict]:
    params = {
        'text': query,
        'page': page,
    }

    if order_by:
        params['order_by'] = order_by

    if experience:
        params['experience'] = experience

    if work_format:
        params['work_format'] = work_format

    if salary_from:
        params['salary_from'] = salary_from

    if work_schedule_by_days:
        params['work_schedule_by_days'] = work_schedule_by_days

    if employment_form:
        params['employment_form'] = employment_form

    page_obj = Fetcher.get(url, params=params, impersonate='chrome')
    _raise_if_captcha(page_obj, url)

    script_tag = page_obj.css('template#HH-Lux-InitialState').first
    data = script_tag.json()
    vacancies = data.get('vacancySearchResult', {}).get('vacancies')

    return [extract_vacancy_data(vac) for vac in vacancies]


def fetch_vacancy_full_description(url: str) -> str:
    page_obj = Fetcher.get(url, impersonate='chrome')
    _raise_if_captcha(page_obj, url)
    desc_block = page_obj.css('[data-qa="vacancy-description"]').first
    if not desc_block:
        return ''
    return desc_block.html_content


def fetch_vacancy_description(url: str) -> str:
    page_obj = Fetcher.get(url, impersonate='chrome')
    _raise_if_captcha(page_obj, url)
    meta_teg = page_obj.css('meta[name="description"]').first

    if not meta_teg:
        return ''

    return meta_teg.attrib.get('content', '')


def fetch_vacancy_skills(url: str) -> list[str]:
    """Извлекает ключевые навыки вакансии со страницы hh.ru (без описания).

    Используется только при детальном парсинге отдельной вакансии, чтобы не
    ходить по карточкам при общем поиске (защита от капчи).
    """
    page_obj = Fetcher.get(url, impersonate='chrome')
    _raise_if_captcha(page_obj, url)

    skills: list[str] = []

    # Сначала пробуем JSON-состояние hh.ru (ключевые навыки часто там).
    try:
        script_tag = page_obj.css('template#HH-Lux-InitialState').first
        if script_tag:
            data = script_tag.json()
            key_skills = (
                data.get('vacancy', {})
                .get('keySkills', [])
                or data.get('keySkills', [])
            )
            for skill in key_skills:
                name = skill.get('name') if isinstance(skill, dict) else skill
                if name:
                    skills.append(str(name))
    except Exception:
        pass

    if not skills:
        # Фоллбэк: селектор из HTML hh.ru.
        for el in page_obj.css('[data-qa="skills-element"]') or []:
            text = el.text().strip()
            if text:
                skills.append(text)

    return skills


def save_vacancy_batch(vacancies_data: list[dict]) -> list[Vacancy]:
    saved_vacancies = []
    for vacancy_data in vacancies_data:
        url = vacancy_data.get('url')
        skills_raw = vacancy_data.pop('_skills', None)
        published_at = vacancy_data.get('published_at')

        vacancy, _ = Vacancy.objects.update_or_create(
            url=url,
            defaults={
                'title': vacancy_data.get('title'),
                'company': vacancy_data.get('company'),
                'location': vacancy_data.get('location'),
                'experience': vacancy_data.get('experience'),
                'description': vacancy_data.get('description', ''),
                'employment': vacancy_data.get('employment'),
                'work_format': vacancy_data.get('work_format'),
                'salary_from': vacancy_data.get('salary_from'),
                'salary_to': vacancy_data.get('salary_to'),
                'source': vacancy_data.get('source'),
                'published_at': published_at,
            },
        )

        if skills_raw:
            _set_vacancy_skills(vacancy, skills_raw)

        saved_vacancies.append(vacancy)

    return saved_vacancies


def save_vacancy(vacancy_data: dict) -> Vacancy:
    vacancy, created = Vacancy.objects.update_or_create(
        url=vacancy_data.get('url'),
        defaults={
            'title': vacancy_data.get('title'),
            'company': vacancy_data.get('company'),
            'location': vacancy_data.get('location'),
            'experience': vacancy_data.get('experience'),
            'description': vacancy_data.get('description', ''),
            'employment': vacancy_data.get('employment'),
            'work_format': vacancy_data.get('work_format'),
            'salary_from': vacancy_data.get('salary_from'),
            'salary_to': vacancy_data.get('salary_to'),
            'source': vacancy_data.get('source'),
            'published_at': vacancy_data.get('published_at'),
        },
    )

    skills_raw = vacancy_data.get('_skills')
    if skills_raw:
        _set_vacancy_skills(vacancy, skills_raw)

    return vacancy


def _set_vacancy_skills(vacancy: Vacancy, skills_raw: list[str]) -> None:
    """Сохраняет навыки вакансии, нормализуя названия через users.Skill."""
    skill_objects = []
    for raw in skills_raw:
        name = Skill.normalize_name(raw)
        if not name:
            continue
        skill = Skill.get_or_create_normalized(name)
        skill_objects.append(skill)
    vacancy.skills.set(skill_objects)


def extract_vacancy_data(vacancy: dict) -> dict:
    work_formats_list = (vacancy.get('workFormats') or [{}])[0].get('workFormatsElement', [])
    salary = extract_salary(vacancy.get('compensation') or {})

    published_at = _parse_published_at(
        vacancy.get('publicationTime')
        or vacancy.get('published_at')
        or vacancy.get('@datePosted')
    )

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
        'published_at': published_at,
    }


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
