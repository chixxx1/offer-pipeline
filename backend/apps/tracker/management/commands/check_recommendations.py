from django.core.management import BaseCommand

from apps.tracker.services.matching import sync_user_recommendations
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Фоновый мониторинг свежих рекомендаций вакансий (под будущий ТГ-бот).'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=int, help='ID пользователя для проверки')
        parser.add_argument(
            '--variant-id',
            type=int,
            default=None,
            help='ID варианта профиля (опционально)',
        )
        parser.add_argument(
            '--fetch',
            action='store_true',
            help='Забирать свежие вакансии с hh.ru (1 запрос к выдаче)',
        )

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        variant_id = options.get('variant_id')
        fetch = options.get('fetch')

        users = User.objects.all()
        if user_id:
            users = users.filter(id=user_id)

        if not users.exists():
            self.stdout.write(self.style.WARNING('Пользователи не найдены.'))
            return

        for user in users:
            variant = None
            if variant_id:
                from apps.users.models import ProfileVariant

                try:
                    variant = ProfileVariant.objects.get(id=variant_id, profile__user=user)
                except ProfileVariant.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Вариант #{variant_id} не найден для пользователя {user.username}'
                        )
                    )
                    continue

            recommendations = sync_user_recommendations(
                user, variant=variant, fetch_from_hh=fetch
            )

            new_count = sum(1 for r in recommendations if r.is_new)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Пользователь {user.username}: '
                    f'рекомендаций {len(recommendations)}, новых {new_count}'
                )
            )
