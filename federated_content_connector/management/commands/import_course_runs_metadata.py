""""Management command to import course metadata for all existing courses."""

from django.core.management import BaseCommand

from federated_content_connector.course_metadata_importer import CourseMetadataImporter


class Command(BaseCommand):
    """Management command to import course metadata for all existing courses"""

    help = "Import course metadata for all existing courses"

    def handle(self, *args, **options):
        CourseMetadataImporter.import_all_courses_metadata()
