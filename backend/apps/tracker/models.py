from encodings import mac_arabic

from django.db import models

# добавить поле требуемого опыта работы в вакансию

class Vacancy(models.Model):
    class Source(models.TextChoices):
        HH = 'hh.ru', 'hh'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Vacancy'
        verbose_name_plural = 'Vacancies'

    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    url = models.URLField()
    location = models.CharField(max_length=30, blank=True, default='')
    experience = models.CharField(max_length=20, blank=True, default='')
    description = models.TextField(null=True, blank=True)
    employment = models.CharField(max_length=20, blank=True, default='')
    source = models.CharField(max_length=20, choices=Source.choices)

    salary_from = models.IntegerField(null=True, blank=True)
    salary_to = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.title}, company {self.company}"


class Application(models.Model):
    class Status(models.TextChoices):
        FOUND = 'found', 'найдено'
        APPLIED = 'applied', 'откликнулся'
        INTERVIEW = 'interview', 'собеседование'
        OFFER = 'offer', 'оффер'
        REJECTED = 'rejected', 'отказ'

    class Meta:
        ordering = ['-created_at']

    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='applications')
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.FOUND)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    applied_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.vacancy}, status {self.status}"
