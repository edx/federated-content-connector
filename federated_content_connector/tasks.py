"""Async tasks for federated_content_connector."""
from logging import getLogger

from celery import shared_task

from federated_content_connector.course_metadata_importer import CourseMetadataImporter

LOGGER = getLogger(__name__)


@shared_task()
def import_course_metadata(courserun_keys):
    """
    Task to fetch course metadata for courseruns represented by `courserun_keys`.

    Arguments:
        courserun_keys (list): courserun keys
    """
    LOGGER.info('[FEDERATED_CONTENT_CONNECTOR] import_course_metadata task triggered')
    CourseMetadataImporter.import_courses_metadata(courserun_keys)
