"""federated_content_connector signals"""
from logging import getLogger

from federated_content_connector.models import CourseDetails
from federated_content_connector.tasks import import_course_metadata

LOGGER = getLogger(__name__)


def handle_courseoverview_import_course_metadata(sender, courserun_key):
    """Handler for CourseOverview.import_course_metadata signal"""
    LOGGER.info("[FEDERATED_CONTENT_CONNECTOR] CourseOverview.import_course_metadata signal received.")

    courserun_keys = [courserun_key]
    import_course_metadata.delay(courserun_keys)


def handle_courseoverview_delete_course_metadata(sender, courserun_key):
    """Handler for CourseOverview.delete_course_metadata signal"""
    LOGGER.info("[FEDERATED_CONTENT_CONNECTOR] CourseOverview.delete_course_metadata signal received.")

    CourseDetails.objects.filter(id=courserun_key).delete()
