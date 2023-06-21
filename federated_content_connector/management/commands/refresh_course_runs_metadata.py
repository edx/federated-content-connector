""""Management command to refresh course metadata."""

import logging
from datetime import datetime, timedelta

from django.core.management import BaseCommand
from django.db.models import Q
from django.utils.timezone import now
from opaque_keys.edx.locator import CourseLocator

from federated_content_connector.course_metadata_importer import CourseMetadataImporter
from federated_content_connector.models import CourseDetails, CourseDetailsImportStatus

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
            course_keys = [course['key'] for course in courses]
            course_data_modified_timestamps.extend([course['data_modified_timestamp'] for course in courses])

            logger.info(f'[REFRESH_COURSE_METADATA] Processing. Courses: [{course_keys}]')

            courserun_locators = cls.courseruns_to_update(course_keys)

            courserun_keys = list(map(str, courserun_locators))
            logger.info(f'[REFRESH_COURSE_METADATA] Updating. Courserun Kyes: [{courserun_keys}]')

            processed_courses_details = CourseMetadataImporter.process_courses_details(courserun_locators, courses)
            CourseMetadataImporter.store_courses_details(processed_courses_details)

            logger.info(f'[REFRESH_COURSE_METADATA] Processing Completed. Courses: [{course_keys}]')

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
    def courseruns_to_update(cls, course_keys):
        """Return a list of courserun locators"""
        # This is equivalent to `course-v1`
        namespace = CourseLocator.CANONICAL_NAMESPACE
        # Convert AA+AA101 to course-v1:AA+AA101
        namespaced_course_keys = map(lambda ck: f'{namespace}:{ck}', course_keys)

        qobjs = Q()
        for course_key in namespaced_course_keys:
            qobjs |= Q(id__istartswith=course_key)

        return list(CourseDetails.objects.filter(qobjs).values_list('id', flat=True))
