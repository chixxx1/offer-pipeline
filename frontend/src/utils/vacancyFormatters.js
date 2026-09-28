const EXPERIENCE_LABELS = {
  noExperience: 'Без опыта',
  between1And3: 'Опыт 1–3 года',
  between3And6: 'Опыт 3–6 лет',
  moreThan6: 'Опыт более 6 лет',
}

const WORK_FORMAT_LABELS = {
  ON_SITE: 'На месте работадателя',
  REMOTE: 'Удалённо',
  HYBRID: 'Гибрид',
  FIELD_WORK: 'Разъездной',
}

const EMPLOYMENT_LABELS = {
  FULL: 'Полная занятость',
  PART: 'Частичная занятость',
  PROJECT: 'Проектная работа',
  VOLUNTEER: 'Волонтёрство',
}

export function formatExperience(code) {
  return EXPERIENCE_LABELS[code] || code || ''
}

export function formatWorkFormat(workFormatString) {
  if (!workFormatString) return ''
  return workFormatString
    .split(', ')
    .map((code) => WORK_FORMAT_LABELS[code] || code)
    .join(', ')
}

export function formatEmployment(code) {
  return EMPLOYMENT_LABELS[code] || code || ''
}

export function formatSalary(salaryFrom, salaryTo) {
  if (!salaryFrom && !salaryTo) return ''
  if (salaryFrom && salaryTo) return `${salaryFrom.toLocaleString('ru')} – ${salaryTo.toLocaleString('ru')} ₽`
  if (salaryFrom) return `от ${salaryFrom.toLocaleString('ru')} ₽`
  return `до ${salaryTo.toLocaleString('ru')} ₽`
}