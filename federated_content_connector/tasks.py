"""Async tasks for federated_content_connector."""
from logging import getLogger

from celery import shared_task
from opaque_keys.edx.keys import CourseKey

from federated_content_connector.course_metadata_importer import CourseMetadataImporter

LOGGER = getLogger(__name__)


@shared_task()
def import_course_metadata(courserun_keys):
    """
    Task to fetch course metadata for courseruns represented by `courserun_keys`.

    Arguments:
        courserun_keys (list): courserun keys
    """
    LOGGER.info(f'[FEDERATED_CONTENT_CONNECTOR] import_course_metadata task triggered: Keys: {courserun_keys}')
    courserun_locators = [CourseKey.from_string(courserun_key) for courserun_key in courserun_keys]
    CourseMetadataImporter.import_specific_courses_metadata(courserun_locators)
