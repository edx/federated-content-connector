"""federated_content_connector signals."""
from logging import getLogger

from federated_content_connector.models import CourseDetails
from federated_content_connector.tasks import import_course_metadata

LOGGER = getLogger(__name__)


def handle_courseoverview_import_course_details(sender, courserun_key, **kwargs):  # pylint: disable=unused-argument
    """Handle CourseOverview.import_course_metadata signal."""
    LOGGER.info(
        f"[FEDERATED_CONTENT_CONNECTOR] CourseOverview.import_course_metadata signal received. Key: [{courserun_key}]"
    )

    courserun_keys = [courserun_key]
    import_course_metadata.delay(courserun_keys)


def handle_courseoverview_delete_course_details(sender, courserun_key, **kwargs):  # pylint: disable=unused-argument
    """Handle CourseOverview.delete_course_metadata signal."""
    LOGGER.info(
        f"[FEDERATED_CONTENT_CONNECTOR] CourseOverview.delete_course_metadata signal received. Key: [{courserun_key}]"
    )
    CourseDetails.objects.filter(id=courserun_key).delete()
