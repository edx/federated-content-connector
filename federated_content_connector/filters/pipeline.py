"""Open edx Filters Pipeline for the federated content connector."""
from django.conf import settings
from openedx.core.djangoapps.catalog.utils import get_course_data
from openedx_filters import PipelineStep

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

    def run_filter(self, course_key, course_home_url):  # pylint: disable=arguments-differ
        """
        Pipeline step that modifies the course home url for externally hosted courses
        """
        course_key_str = '{}+{}'.format(course_key.org, course_key.course)
        course_data = get_course_data(course_key_str, ['course_type', 'product_source'])
        if course_data:
            course_type = course_data.get('course_type')
            product_source = course_data.get('product_source')
            product_source_slug = product_source['slug'] if isinstance(product_source, dict) else product_source
            if course_type == EXEC_ED_COURSE_TYPE and product_source_slug == PRODUCT_SOURCE_2U:
                course_home_url = getattr(settings, 'EXEC_ED_LANDING_PAGE', EXEC_ED_LANDING_PAGE)

        return {'course_key': course_key, 'course_home_url': course_home_url}
