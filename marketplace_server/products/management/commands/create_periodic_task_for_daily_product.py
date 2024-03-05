from django.core.management import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class Command(BaseCommand):

    def handle(self, *args, **options) -> None:
        task_name = "Update daily special product"
        crontab_schedule = CrontabSchedule.objects.create(
            minute="0",
            hour="2",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*"
        )

        PeriodicTask.objects.create(
            name=task_name,
            task="products.tasks.product_is_daily_special",
            crontab=crontab_schedule,
        )
