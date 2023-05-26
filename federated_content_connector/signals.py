"""federated_content_connector signals"""
from logging import getLogger

from federated_content_connector.course_metadata_importer import CourseMetadataImporter
from federated_content_connector.models import CourseDetails

log = getLogger(__name__)


def handle_courseoverview_import_course_metadata(sender, courserun_key):
    """Handler for CourseOverview.import_course_metadata signal"""
    log.info("[FEDERATED_CONTENT_CONNECTOR] CourseOverview.import_course_metadata signal recived.")

    # TODO: Move all the below code into an async task and then trigger that task from here
    courserun_keys = [courserun_key]
    CourseMetadataImporter.import_courses_metadata(courserun_keys)


def handle_courseoverview_delete_course_metadata(sender, courserun_key):
    """Handler for CourseOverview.delete_course_metadata signal"""
    log.info("[FEDERATED_CONTENT_CONNECTOR] CourseOverview.delete_course_metadata signal recived.")

    CourseDetails.objects.filter(id=courserun_key).delete()
