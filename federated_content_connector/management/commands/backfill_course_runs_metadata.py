""""Management command to backfill course metadata for all existing courses"""

from django.core.management import BaseCommand

from federated_content_connector.course_metadata_importer import CourseMetadataImporter


class Command(BaseCommand):
    """Management command to backfill course metadata for all existing courses"""

    help = "Backfill course metadata for all existing courses"

    # lint-amnesty, pylint: disable=bad-option-value, unicode-format-string
    def handle(self, *args, **options):  # lint-amnesty, pylint: disable=too-many-statements
        CourseMetadataImporter.import_courses_metadata()
