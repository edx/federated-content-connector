from openedx_filters import PipelineStep
from openedx_filters.learning.filters import CourseHomeUrlCreationStarted
from openedx.core.djangoapps.catalog.utils import get_course_data

from federated_content_connector.constants import EXEC_ED_COURSE_TYPE, EXEC_ED_LANDING_PAGE, PRODUCT_SOURCE_2U


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

    def run_filter(self, course_key, course_home_url):
        """
        Pipeline step that modifies the course home url for externally hosted courses
        """

        course_key_str = '{}+{}'.format(course_key.org, course_key.course)
        course_data = get_course_data(course_key_str, ['course_type', 'product_source'])
        if course_data:
            course_type = course_data.get('course_type')
            product_source = course_data.get('product_source')
            if course_type == EXEC_ED_COURSE_TYPE and product_source == PRODUCT_SOURCE_2U:
                return {'course_key': course_key, 'course_home_url': EXEC_ED_LANDING_PAGE}

        raise CourseHomeUrlCreationStarted.PreventCourseHomeUrlRewrite()
