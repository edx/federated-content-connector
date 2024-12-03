"""Open edx Filters Pipeline for the federated content connector."""
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from openedx.core.djangoapps.catalog.utils import get_course_data
from openedx_filters import PipelineStep
from pytz import utc

from federated_content_connector.constants import EXEC_ED_COURSE_TYPE, EXEC_ED_LANDING_PAGE, PRODUCT_SOURCE_2U
from federated_content_connector.models import CourseDetails


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

        course_details = CourseDetails.objects.filter(id=course_key).first()
        if course_details:
            course_type = course_details.course_type
            product_source = course_details.product_source
        else:
            course_type, product_source = self._fetch_course_type_and_product_source(course_key)

        if course_type == EXEC_ED_COURSE_TYPE and product_source == PRODUCT_SOURCE_2U:
            filtered_course_home_url = getattr(settings, 'EXEC_ED_LANDING_PAGE', EXEC_ED_LANDING_PAGE)

        return {'course_key': course_key, 'course_home_url': filtered_course_home_url}

    def _fetch_course_type_and_product_source(self, course_key):
        """
        Helper to determine the course_type and product_source
        from the course-discovery service.
        """
        course_key_str = '{}+{}'.format(course_key.org, course_key.course)
        course_data = get_course_data(course_key_str, ['course_type', 'product_source'])

        if not course_data:
            return (None, None)

        course_type = course_data.get('course_type')
        product_source_value = course_data.get('product_source')
        product_source = product_source_value
        if isinstance(product_source_value, dict):
            product_source = product_source_value['slug']

        return course_type, product_source


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
        try:
            course_details = CourseDetails.objects.get(id=course_key)
            course_type = course_details.course_type
            product_source = course_details.product_source
            start_date = course_details.start_date
            if product_source == PRODUCT_SOURCE_2U and course_type == EXEC_ED_COURSE_TYPE:
                if start_date and start_date <= timezone.now():
                    serialized_enrollment['hasStarted'] = True
        except CourseDetails.DoesNotExist:
            pass

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
        try:
            course_details = CourseDetails.objects.get(id=serialized_courserun.get('courseId'))
            course_type = course_details.course_type
            product_source = course_details.product_source
            homeUrl = serialized_courserun.get('homeUrl')
            start_date, end_date = course_details.start_date, course_details.end_date

            if product_source == PRODUCT_SOURCE_2U and course_type == EXEC_ED_COURSE_TYPE:
                now_utc = datetime.now(utc)
                serialized_courserun.update({
                    'startDate': start_date,
                    'endDate': end_date,
                    'isStarted': now_utc > start_date if start_date is not None else True,
                    'isArchived': now_utc > end_date if end_date is not None else False,
                    'resumeUrl': homeUrl
                })

        except CourseDetails.DoesNotExist:
            pass

        return {'serialized_courserun': serialized_courserun}
