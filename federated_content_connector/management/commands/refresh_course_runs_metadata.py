""""Management command to refresh course metadata."""

import logging
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.utils.timezone import now

from federated_content_connector.course_metadata_importer import CourseMetadataImporter
from federated_content_connector.models import CourseDetailsImportStatus

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to refresh course metadata"""

    help = "Refresh course metadata"

    def handle(self, *args, **options):
        self.refresh_courses_metadata()

    @classmethod
    def refresh_courses_metadata(cls):
        """Refresh courses updated after last refresh."""
        timestamp_format = CourseDetailsImportStatus.TIMESTAMP_FORMAT
        course_data_modified_timestamps = []

        last_successful_import_timestamp = CourseDetailsImportStatus.last_successful_import_timestamp()
        # This will be true only once in a lifetime
        if last_successful_import_timestamp is None:
            logger.info('[REFRESH_COURSE_METADATA] No previous timstamp found.')
            timestamp = now() - timedelta(hours=1)
            last_successful_import_timestamp = timestamp.strftime(timestamp_format)
            CourseDetailsImportStatus.save_last_successful_import_timestamp(last_successful_import_timestamp)

        logger.info(f'[REFRESH_COURSE_METADATA] Refresh Started. Timestamp: [{last_successful_import_timestamp}]')

        for courses in CourseMetadataImporter.courses(last_successful_import_timestamp):
            course_data_modified_timestamps.extend([course['data_modified_timestamp'] for course in courses])

            courserun_with_course_uuids = cls.courseruns_to_update(courses)
            courserun_keys = courserun_with_course_uuids.keys()

            logger.info(f'[REFRESH_COURSE_METADATA] Processing. Courseruns: [{courserun_keys}]')

            processed_courses_details = CourseMetadataImporter.process_courses_details(
                courses,
                courserun_with_course_uuids
            )
            CourseMetadataImporter.store_courses_details(processed_courses_details)

            logger.info(f'[REFRESH_COURSE_METADATA] Processing Completed. Courseruns: [{courserun_keys}]')

        # Sort course timestamps in descending order and store first timestamp as last_successful_import_timestamp
        if course_data_modified_timestamps:
            logger.info(f'[REFRESH_COURSE_METADATA] All Course Timestamps: [{course_data_modified_timestamps}]')
            sorted_timestamps = sorted(
                course_data_modified_timestamps,
                key=lambda timestamp: datetime.strptime(timestamp, timestamp_format),
                reverse=True
            )
            next_timestamp = sorted_timestamps[0]
            CourseDetailsImportStatus.save_last_successful_import_timestamp(next_timestamp)

            logger.info(f'[REFRESH_COURSE_METADATA] Next Timestamp: [{next_timestamp}]')

        logger.info('[REFRESH_COURSE_METADATA] Refresh Completed.')

    @classmethod
    def courseruns_to_update(cls, courses):
        """Return a map of courserun key and course uuid."""
        courserun_with_course_uuids = {}
        for course in courses:
            for courserun in course.get('course_runs', []):
                courserun_with_course_uuids[courserun.get('key')] = courserun.get('course_uuid')

        return courserun_with_course_uuids
