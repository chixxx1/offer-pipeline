from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Skill(models.Model):

    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, db_index=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    @classmethod
    def normalize_name(cls, raw_name: str) -> str:
        return ' '.join(raw_name.strip().lower().split())

    @classmethod
    def get_or_create_normalized(cls, raw_name: str) -> 'Skill':
        name = cls.normalize_name(raw_name)
        if not name:
            raise ValueError('Название навыка не может быть пустым')
        skill, _ = cls.objects.get_or_create(
            name=name,
            defaults={'slug': slugify(name, allow_unicode=True) or name},
        )
        return skill

    def save(self, *args, **kwargs):
        self.name = self.normalize_name(self.name)
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or self.name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Profile(models.Model):

    class WorkFormat(models.TextChoices):
        REMOTE = 'remote', 'удалённо'
        OFFICE = 'office', 'офис'
        HYBRID = 'hybrid', 'гибрид'
        ANY = 'any', 'любой'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_profile',
    )
    about = models.TextField(blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    desired_salary = models.PositiveIntegerField(null=True, blank=True)
    work_format = models.CharField(
        max_length=20, choices=WorkFormat.choices, default=WorkFormat.ANY, db_index=True
    )
    github_url = models.URLField(blank=True, default='')
    linkedin_url = models.URLField(blank=True, default='')
    telegram = models.CharField(max_length=100, blank=True, default='')
    contact_email = models.EmailField(blank=True, default='')
    skills = models.ManyToManyField(Skill, blank=True, related_name='profiles')

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    @classmethod
    def get_for_user(cls, user) -> 'Profile':
        profile, _ = cls.objects.get_or_create(user=user)
        return profile

    def __str__(self) -> str:
        return f'profile: {self.user.username}'


class WorkExperience(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-is_current', '-start_date']
        verbose_name = 'Work experience'
        verbose_name_plural = 'Work experiences'

    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': 'Дата окончания не может быть раньше даты начала.'})

    def __str__(self) -> str:
        return f'{self.position} в {self.company}'


class Education(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=200)
    degree = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['-start_year']
        verbose_name = 'Education'
        verbose_name_plural = 'Education'

    def clean(self):
        if self.end_year is not None and self.start_year and self.end_year < self.start_year:
            raise ValidationError({'end_year': 'Год окончания не может быть раньше года начала.'})

    def __str__(self) -> str:
        return f'{self.degree}, {self.institution}'


class ProfileVariant(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='variants')
    title = models.CharField(max_length=150)
    about = models.TextField(blank=True, default='')
    skills = models.ManyToManyField(Skill, blank=True, related_name='profile_variants')
    experiences = models.ManyToManyField(
        WorkExperience, blank=True, related_name='profile_variants'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Profile variant'
        verbose_name_plural = 'Profile variants'

    def __str__(self) -> str:
        return f'{self.title} ({self.profile.user.username})'


def validate_resume_file(file) -> None:
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        raise ValidationError('Размер файла не должен превышать 10 МБ.')
    extension = file.name.lower().rsplit('.', 1)[-1] if '.' in file.name else ''
    if extension not in ('pdf', 'docx'):
        raise ValidationError('Разрешены только файлы .pdf и .docx.')


class ResumeFile(models.Model):

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resumes')
    variant = models.ForeignKey(
        ProfileVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resumes',
    )
    file = models.FileField(upload_to='resumes/%Y/%m/', validators=[validate_resume_file])
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Resume file'
        verbose_name_plural = 'Resume files'

    def save(self, *args, **kwargs):
        if self.pk is None and self.file and self.file.name and not self.file._committed:
            extension = self.file.name.lower().rsplit('.', 1)[-1] if '.' in self.file.name else ''
            self.file.name = f'resume_{self.profile.user_id}.{extension}'
        if not self.original_name:
            self.original_name = getattr(self.file, 'original_name', '') or self.file.name
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        storage, name = self.file.storage, self.file.name
        super().delete(*args, **kwargs)
        if name and storage.exists(name):
            storage.delete(name)

    def __str__(self) -> str:
        return f'resume: {self.original_name} ({self.profile.user.username})'
