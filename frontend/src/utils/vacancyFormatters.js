export const EXPERIENCE_OPTIONS = [
  { value: "noExperience", label: "Без опыта" },
  { value: "between1And3", label: "Опыт 1–3 года" },
  { value: "between3And6", label: "Опыт 3–6 лет" },
  { value: "moreThan6", label: "Опыт более 6 лет" },
];

export const WORK_FORMAT_OPTIONS = [
  { value: "ON_SITE", label: "На месте работодателя" },
  { value: "REMOTE", label: "Удалённо" },
  { value: "HYBRID", label: "Гибрид" },
  { value: "FIELD_WORK", label: "Разъездной" },
];

export const WORK_SCHEDULE_OPTIONS = [
  { value: "fullDay", label: "Полный день" },
  { value: "shift", label: "Сменный график" },
  { value: "flexible", label: "Гибкий график" },
  { value: "remote", label: "Удаленная работа" },
  { value: "flyInFlyOut", label: "Вахтовый метод" },
];

export const EMPLOYMENT_FORM_OPTIONS = [
  { value: "full", label: "Полная занятость" },
  { value: "part", label: "Частичная занятость" },
  { value: "project", label: "Проектная работа" },
  { value: "probation", label: "Стажировка" },
];

const createLabelMap = (options) =>
  Object.fromEntries(options.map((opt) => [opt.value, opt.label]));

const EXPERIENCE_LABELS = createLabelMap(EXPERIENCE_OPTIONS);
const WORK_FORMAT_LABELS = createLabelMap(WORK_FORMAT_OPTIONS);
const WORK_SCHEDULE_LABELS = createLabelMap(WORK_SCHEDULE_OPTIONS);
const EMPLOYMENT_LABELS = createLabelMap(EMPLOYMENT_FORM_OPTIONS);

const formatByMap = (code, map) => {
  if (!code) return "";
  const targetCode = Array.isArray(code) ? code[0] : code;
  return map[targetCode] || targetCode;
};

export function formatExperience(code) {
  return formatByMap(code, EXPERIENCE_LABELS);
}

export function formatWorkFormat(input) {
  if (!input) return "";

  const items = Array.isArray(input) ? input : String(input).split(",");

  return items
    .map((code) => formatByMap(code.trim(), WORK_FORMAT_LABELS))
    .filter(Boolean)
    .join(", ");
}

export function formatSchedule(code) {
  return formatByMap(code, WORK_SCHEDULE_LABELS);
}

export function formatEmployment(code) {
  return formatByMap(code, EMPLOYMENT_LABELS);
}

export function formatSalary(salaryFrom, salaryTo) {
  if (!salaryFrom && !salaryTo) return "";

  const formatNum = (n) => (n ? Number(n).toLocaleString("ru-RU") : "");

  if (salaryFrom && salaryTo) {
    return `${formatNum(salaryFrom)} – ${formatNum(salaryTo)} ₽`;
  }
  if (salaryFrom) {
    return `от ${formatNum(salaryFrom)} ₽`;
  }
  return `до ${formatNum(salaryTo)} ₽`;
}
