"""Сервис мэтчинга вакансий и авто-поиска по скиллам."""

from __future__ import annotations

import re
from typing import Any

from django.utils import timezone

from apps.parsing.services.hh_parser import search_vacancies, save_vacancy_batch
from apps.tracker.models import Vacancy, VacancyRecommendation
from apps.users.models import Skill


# Веса критериев мэтчинга (сумма = 100).
SKILLS_MAX_SCORE = 65
SALARY_MAX_SCORE = 15
WORK_FORMAT_MAX_SCORE = 10
CITY_MAX_SCORE = 10


def _normalize(text: str) -> str:
    return ' '.join(str(text or '').strip().lower().split())


def _skill_names(skills_qs) -> list[str]:
    """Возвращает нормализованные названия навыков queryset'а Skill."""
    return [Skill.normalize_name(s.name) for s in skills_qs.all()]


def _last_position(profile) -> str | None:
    """Последняя должность из WorkExperience (текущая, либо по -start_date)."""
    last = (
        profile.experiences.filter(is_current=True).first()
        or profile.experiences.order_by('-start_date').first()
    )
    return last.position if last else None


def build_search_query_from_profile(profile, variant=None) -> dict:
    """Собирает параметры поиска вакансий из профиля (и опционального варианта).

    Поисковый запрос `text` опирается в первую очередь на навыки пользователя
    (или навыки variant, если выбран). Фоллбэк — последняя должность.
    Автоматически подставляются work_format из профиля и order_by по дате
    публикации, чтобы находить самые свежие вакансии.
    """
    if variant is not None:
        skills = _skill_names(variant.skills)
        title = variant.title or ''
    else:
        skills = _skill_names(profile.skills)
        title = ''

    parts = list(skills)
    if title:
        # Навыки, которые уже входят в заголовок варианта, не дублируем отдельно.
        title_norm = _normalize(title)
        extra_skills = [s for s in skills if s not in title_norm]
        parts = extra_skills + [title]

    text = ' '.join(parts) if parts else (_last_position(profile) or '')

    params: dict[str, Any] = {
        'text': text,
        'page': 0,
        'order_by': 'publication_time',
    }

    if profile.work_format and profile.work_format != 'any':
        params['work_format'] = [profile.work_format]

    return params


def _match_skills(vacancy_skills_names: list[str], profile_skills_names: list[str]):
    """Сравнивает навыки профиля с навыками вакансии.

    Возвращает (matched, missing, skill_score, matched_names).
    Учитывает как прямые совпадения навыков, так и точные вхождения названий
    навыков в заголовок/сниппет/описание вакансии.
    """
    vacancy_set = {_normalize(s) for s in vacancy_skills_names}
    profile_set = {_normalize(s) for s in profile_skills_names}

    matched: list[str] = []
    missing: list[str] = []

    for skill in profile_skills_names:
        norm = _normalize(skill)
        if not norm:
            continue
        if norm in vacancy_set:
            matched.append(skill)
            continue
        # Точное вхождение названия навыка в текстовые поля вакансии.
        if any(norm in _normalize(vs) for vs in vacancy_skills_names):
            matched.append(skill)
            continue
        missing.append(skill)

    max_skill_score = SKILLS_MAX_SCORE
    if profile_set:
        skill_score = int(round((len(matched) / len(profile_set)) * max_skill_score))
    else:
        skill_score = 0
    skill_score = min(skill_score, max_skill_score)

    return matched, missing, skill_score


def _match_salary(vacancy, profile) -> tuple[int, list[str]]:
    """Сравнение зарплаты с желаемой (до SALARY_MAX_SCORE баллов)."""
    reasons: list[str] = []
    desired = profile.desired_salary
    if not desired:
        return 0, reasons

    v_from = vacancy.salary_from
    v_to = vacancy.salary_to

    if v_from is None and v_to is None:
        return 0, reasons

    # Берём "предлагаемую" зарплату: верхнюю границу, если есть, иначе нижнюю.
    offered = v_to if v_to is not None else v_from

    if offered is None:
        return 0, reasons

    if offered >= desired:
        score = SALARY_MAX_SCORE
        reasons.append(f'Зарплата {offered} >= желаемой {desired}')
    elif offered >= desired * 0.9:
        score = int(SALARY_MAX_SCORE * 0.7)
        reasons.append(f'Зарплата {offered} близка к желаемой {desired}')
    elif offered >= desired * 0.75:
        score = int(SALARY_MAX_SCORE * 0.4)
        reasons.append(f'Зарплата {offered} ниже желаемой {desired}')
    else:
        score = 0
        reasons.append(f'Зарплата {offered} значительно ниже желаемой {desired}')

    return score, reasons


def _match_work_format(vacancy, profile) -> tuple[int, list[str]]:
    """Сравнение формата работы (до WORK_FORMAT_MAX_SCORE баллов)."""
    reasons: list[str] = []
    profile_format = profile.work_format or 'any'
    if profile_format == 'any':
        return WORK_FORMAT_MAX_SCORE, reasons

    vacancy_format = _normalize(vacancy.work_format)
    if not vacancy_format:
        return 0, reasons

    if profile_format in vacancy_format or vacancy_format in profile_format:
        score = WORK_FORMAT_MAX_SCORE
        reasons.append(f'Формат работы совпадает: {vacancy.work_format}')
    elif profile_format == 'remote' and 'remote' in vacancy_format:
        score = WORK_FORMAT_MAX_SCORE
        reasons.append('Удалённая работа подходит')
    elif profile_format == 'hybrid' and ('hybrid' in vacancy_format or 'remote' in vacancy_format):
        score = int(WORK_FORMAT_MAX_SCORE * 0.7)
        reasons.append('Формат работы частично подходит')
    else:
        score = 0
        reasons.append(f'Формат работы не совпадает: {vacancy.work_format}')

    return score, reasons


def _match_city(vacancy, profile) -> tuple[int, list[str]]:
    """Сравнение города (до CITY_MAX_SCORE баллов). Удалёнка — полный балл."""
    reasons: list[str] = []
    profile_city = _normalize(profile.city)
    vacancy_city = _normalize(vacancy.location)

    if not profile_city:
        return 0, reasons

    # Удалённая работа — полный балл независимо от города.
    vacancy_format = _normalize(vacancy.work_format)
    if 'remote' in vacancy_format:
        return CITY_MAX_SCORE, ['Удалённая работа — город не важен']

    if not vacancy_city:
        return 0, reasons

    if profile_city == vacancy_city:
        return CITY_MAX_SCORE, [f'Город совпадает: {vacancy.location}']

    # Частичное совпадение (подстрока).
    if profile_city in vacancy_city or vacancy_city in profile_city:
        return int(CITY_MAX_SCORE * 0.6), [f'Город частично совпадает: {vacancy.location}']

    return 0, [f'Город не совпадает: {vacancy.location}']


def calculate_vacancy_match(vacancy, profile, variant=None) -> dict:
    """Рассчитывает оценку мэтчинга вакансии для профиля.

    Возвращает {"score", "matched_skills", "missing_skills", "reasons"}.
    """
    if variant is not None:
        profile_skills = _skill_names(variant.skills)
    else:
        profile_skills = _skill_names(profile.skills)

    vacancy_skills = _skill_names(vacancy.skills)

    matched, missing, skill_score = _match_skills(vacancy_skills, profile_skills)

    # Дополнительно: ищем точные вхождения навыков профиля в текстовые поля вакансии,
    # чтобы добавить их в matched, даже если они не в vacancy.skills.
    searchable_text = (
        _normalize(vacancy.title)
        + ' '
        + _normalize(getattr(vacancy, 'snippet', '') or '')
        + ' '
        + _normalize(vacancy.description or '')
    )
    for skill in profile_skills:
        if not skill:
            continue
        if skill in matched:
            continue
        if skill and skill in searchable_text:
            matched.append(skill)
            if skill in missing:
                missing.remove(skill)

    # Пересчитаем skill_score после дополнений.
    if profile_skills:
        skill_score = int(round((len(matched) / len(profile_skills)) * SKILLS_MAX_SCORE))
    skill_score = min(skill_score, SKILLS_MAX_SCORE)

    salary_score, salary_reasons = _match_salary(vacancy, profile)
    work_format_score, work_format_reasons = _match_work_format(vacancy, profile)
    city_score, city_reasons = _match_city(vacancy, profile)

    score = skill_score + salary_score + work_format_score + city_score
    score = min(score, 100)

    reasons: list[str] = []
    if matched:
        reasons.append(f'Совпадение навыков: {", ".join(matched)}')
    if missing:
        reasons.append(f'Отсутствуют навыки: {", ".join(missing)}')
    reasons.extend(salary_reasons)
    reasons.extend(work_format_reasons)
    reasons.extend(city_reasons)

    return {
        'score': score,
        'matched_skills': matched,
        'missing_skills': missing,
        'reasons': reasons,
    }


def sync_user_recommendations(user, variant=None, fetch_from_hh=False):
    """Синхронизирует рекомендации пользователя.

    Если fetch_from_hh=True — делает 1 запрос к выдаче hh.ru (page=0,
    order_by=publication_time), сохраняет вакансии в БД с published_at.
    Рассчитывает мэтчинг и сохраняет подходящие вакансии в
    VacancyRecommendation, не затирая is_new=False и is_dismissed=True у
    уже существующих записей.
    """
    profile = user.user_profile

    saved_vacancies: list[Vacancy] = []
    if fetch_from_hh:
        params = build_search_query_from_profile(profile, variant=variant)
        query = params.pop('text', '')
        page = params.pop('page', 0)
        order_by = params.pop('order_by', None)

        vacancies_data = search_vacancies(
            'https://hh.ru/search/vacancy/',
            query,
            page=page,
            order_by=order_by,
            **params,
        )
        saved_vacancies = save_vacancy_batch(vacancies_data)
    else:
        saved_vacancies = list(Vacancy.objects.all())

    recommendations = []
    for vacancy in saved_vacancies:
        match = calculate_vacancy_match(vacancy, profile, variant=variant)

        rec, created = VacancyRecommendation.objects.update_or_create(
            user=user,
            vacancy=vacancy,
            variant=variant,
            defaults={
                'score': match['score'],
                'matched_skills': match['matched_skills'],
                'missing_skills': match['missing_skills'],
                'reasons': match['reasons'],
            },
        )

        # Не затираем флаги у уже существующих записей.
        if created:
            rec.is_new = True
            rec.is_dismissed = False
            rec.save(update_fields=['is_new', 'is_dismissed'])

        recommendations.append(rec)

    return recommendations
