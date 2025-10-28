from django.core.management.base import BaseCommand
from api.tasks import ingest_data_task

class Command(BaseCommand):
    help = 'Ingests customer and loan data from Excel files into the database'

    def handle(self, *args, **options):
        ingest_data_task.delay()
        self.stdout.write(self.style.SUCCESS('Data ingestion task has been queued.'))