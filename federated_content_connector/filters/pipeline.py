"""Open edx Filters Pipeline for the federated content connector."""
from collections import namedtuple
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from openedx.core.djangoapps.catalog.utils import get_course_data
from openedx_filters import PipelineStep
from pytz import utc

from federated_content_connector.constants import EXEC_ED_COURSE_TYPE, EXEC_ED_LANDING_PAGE, PRODUCT_SOURCE_2U
from federated_content_connector.models import CourseDetails


COURSE_DETAILS_FIELDS = [
    'id',
    'course_key',
    'course_type',
    'product_source',
    'start_date',
    'end_date',
    'enroll_by',
]

CourseDetailsData = namedtuple(
    'CourseDetailsData',
    COURSE_DETAILS_FIELDS,
)


def generate_course_details_data(course_key):
    """
    Given a course_key, generates an instance of ``CourseDetailsData``,
    populated with data read from either a ``CourseDetails`` model instance,
    or a dictionary of data returned by ``get_course_data()``, which is implemented
    as an HTTP call to the course-discovery service.
    """
    model_instance = CourseDetails.objects.filter(id=course_key).first()
    if model_instance:
        return CourseDetailsData(**{
            field_name: getattr(model_instance, field_name, None)
            for field_name in COURSE_DETAILS_FIELDS
        })

    course_key_str = '{}+{}'.format(course_key.org, course_key.course)
    course_data_dict = get_course_data(course_key_str, ['course_type', 'product_source'])
    fields_and_values = {
        field_name: course_data_dict.get(field_name)
        for field_name in COURSE_DETAILS_FIELDS
    }
    product_source_value = fields_and_values.get('product_source')
    if isinstance(product_source_value, dict):
        fields_and_values['product_source'] = product_source_value.get('slug')
    return CourseDetailsData(**fields_and_values)


class CreateCustomUrlForCourseStep(PipelineStep):
    """
    Step that modifies the url for the course home page.

    Example usage:

    Add the following configurations to your configuration file:

        "OPEN_EDX_FILTERS_CONFIG": {
            "org.openedx.learning.course.homepage.url.creation.started.v1": {
                "fail_silently": False,
                "pipeline": [
                    "federated_content_connector.filters.pipeline.CreateCustomUrlForCourseStep"
                ]
            }
        }
    """

    def run_filter(self, course_key, course_home_url):  # pylint: disable=arguments-differ
        """
        Pipeline step that modifies the course home url for externally hosted courses
        """
        filtered_course_home_url = course_home_url

        course_details = generate_course_details_data(course_key)
        if is_exec_ed_2u_course(course_details):
            filtered_course_home_url = getattr(
                settings, 'EXEC_ED_LANDING_PAGE', EXEC_ED_LANDING_PAGE,
            )

        return {'course_key': course_key, 'course_home_url': filtered_course_home_url}


def is_exec_ed_2u_course(course_details_data):
    return (
        course_details_data.product_source == PRODUCT_SOURCE_2U and
        course_details_data.course_type == EXEC_ED_COURSE_TYPE
    )


class CreateApiRenderEnrollmentStep(PipelineStep):
    """
    Step that modifies the enrollment data for the course.

    Example usage:

    Add the following configurations to your configuration file:

        "OPEN_EDX_FILTERS_CONFIG": {
            "org.openedx.learning.home.enrollment.api.rendered.v1": {
                "fail_silently": False,
                "pipeline": [
                    "federated_content_connector.filters.pipeline.CreateApiRenderEnrollmentStep"
                ]
            }
        }
    """

    def run_filter(self, course_key, serialized_enrollment):  # pylint: disable=arguments-differ
        """
        Pipeline step that modifies the enrollment data for the course.
        """
        course_details = generate_course_details_data(course_key)
        start_date = course_details.start_date
        if is_exec_ed_2u_course(course_details):
            if start_date and start_date <= timezone.now():
                serialized_enrollment['hasStarted'] = True

        return {'course_key': course_key, 'serialized_enrollment': serialized_enrollment}


class CreateApiRenderCourseRunStep(PipelineStep):
    """
    Step that modifies the courserun data for the course.

    Example usage:

    Add the following configurations to your configuration file:

        "OPEN_EDX_FILTERS_CONFIG": {
            "org.openedx.learning.home.courserun.api.rendered.started.v1": {
                "fail_silently": False,
                "pipeline": [
                    "federated_content_connector.filters.pipeline.CreateApiRenderCourseRunStep"
                ]
            }
        }
    """

    def run_filter(self, serialized_courserun):  # pylint: disable=arguments-differ
        """
        Pipeline step that modifies the courserun data for the course.
        """
        course_details = generate_course_details_data(serialized_courserun.get('courseId'))
        homeUrl = serialized_courserun.get('homeUrl')
        start_date, end_date = course_details.start_date, course_details.end_date

        if is_exec_ed_2u_course(course_details):
            now_utc = datetime.now(utc)
            serialized_courserun.update({
                'startDate': start_date,
                'endDate': end_date,
                'isStarted': now_utc > start_date if start_date is not None else True,
                'isArchived': now_utc > end_date if end_date is not None else False,
                'resumeUrl': homeUrl
            })

        return {'serialized_courserun': serialized_courserun}
