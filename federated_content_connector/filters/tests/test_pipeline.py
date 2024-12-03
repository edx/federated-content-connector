"""
Test cases for Pipeline.
"""
from unittest.mock import Mock, patch

from ddt import data, ddt, unpack
from django.test import TestCase, override_settings
from opaque_keys.edx.keys import CourseKey
from openedx_filters.learning.filters import CourseHomeUrlCreationStarted

from federated_content_connector.constants import EXEC_ED_COURSE_TYPE, EXEC_ED_LANDING_PAGE, PRODUCT_SOURCE_2U
from federated_content_connector.models import CourseDetails


@override_settings(
    OPEN_EDX_FILTERS_CONFIG={
        "org.openedx.learning.course.homepage.url.creation.started.v1": {
            "fail_silently": False,
            "pipeline": [
                "federated_content_connector.filters.pipeline.CreateCustomUrlForCourseStep"
            ]
        }
    },
)
@ddt
class CreateCustomUrlForCourseStepTestCase(TestCase):
    """
    The course url at the backend will be filtered and passed according to course type
    """

    def setUp(self):
        super().setUp()
        self.mock_user = Mock()
        self.course_key = CourseKey.from_string("course-v1:Demo+DemoX+Demo_Course")
        self.course_home_url = 'www.edx.org'
        CourseDetails.objects.all().delete()

    @data(
        ({'course_type': EXEC_ED_COURSE_TYPE, 'product_source': {'slug': PRODUCT_SOURCE_2U}}, EXEC_ED_LANDING_PAGE),
        ({'course_type': 'audit', 'product_source': {'slug': 'edx'}}, 'www.edx.org')
    )
    @unpack
    @patch('federated_content_connector.filters.pipeline.get_course_data')
    def test_create_course_url(self, course_data, expected_url, mock_get_course_data):
        """
        Check course type belongs to executive or audit.
        """
        mock_get_course_data.return_value = course_data
        expected_result = self.course_key, expected_url

        result = CourseHomeUrlCreationStarted.run_filter(
            course_key=self.course_key,
            course_home_url=self.course_home_url,
        )
        self.assertEqual(result, expected_result)

    @patch('federated_content_connector.filters.pipeline.get_course_data')
    def test_create_course_url_from_model(self, mock_get_course_data):
        """
        Check course type belongs to executive or audit.
        """
        CourseDetails.objects.get_or_create(
            id=self.course_key,
            course_type=EXEC_ED_COURSE_TYPE,
            product_source=PRODUCT_SOURCE_2U,
        )

        result = CourseHomeUrlCreationStarted.run_filter(
            course_key=self.course_key,
            course_home_url=self.course_home_url,
        )
        expected_result = self.course_key, EXEC_ED_LANDING_PAGE
        self.assertEqual(result, expected_result)
        self.assertFalse(mock_get_course_data.called)
