"""
Tests for `import_course_runs_metadata` management command.
"""
import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from opaque_keys.edx.keys import CourseKey

from federated_content_connector.management.commands import import_course_runs_metadata
from federated_content_connector.management.commands.import_course_runs_metadata import CourseMetadataImporter
from federated_content_connector.management.commands.tests.test_utils import side_effect_func
from federated_content_connector.models import CourseDetails


@pytest.mark.django_db
class TestImportCourserunsMetadataCommand(TestCase):
    """
    Tests `import_course_runs_metadata` management command.
    """

    def setUp(self):
        super().setUp()
        self.command = import_course_runs_metadata.Command()

    def courserun_locators(self):
        """
        Return list of course locators.
        """
        return [
            CourseKey.from_string("course-v1:edX+DemoX+Demo_Course2024a"),
            CourseKey.from_string("course-v1:edX+E2E-101+course"),
        ]

    @patch.object(CourseMetadataImporter, 'get_api_client')
    @patch.object(CourseMetadataImporter, 'courserun_locators_to_import')
    def test_command(self, mocked_courserun_locators_to_import, mocked_get_api_client):
        """
        Verify that command work as expected.
        """
        assert CourseDetails.objects.count() == 0

        mocked_get_api_client.return_value = MagicMock()
        mocked_get_api_client.return_value.get = MagicMock(side_effect=side_effect_func)
        # mocked_get_api_client.return_value.get = MagicMock(return_value=MockResponse())
        mocked_courserun_locators_to_import.return_value = self.courserun_locators()

        call_command(self.command)

        assert CourseDetails.objects.count() == 2

        course_details = CourseDetails.objects.get(id=self.courserun_locators()[0])
        assert course_details.course_key == 'edX+DemoX'
        assert course_details.course_type == 'executive-education-2u'
        assert course_details.product_source == '2u'
        assert course_details.start_date.replace(tzinfo=None) == datetime.datetime(2024, 3, 14, 0, 0, 0)
        assert course_details.end_date.replace(tzinfo=None) == datetime.datetime(2024, 5, 27, 23, 59, 59)
        assert course_details.enroll_by.replace(tzinfo=None) == datetime.datetime(2024, 3, 31, 0, 0, 0)

        course_details = CourseDetails.objects.get(id=self.courserun_locators()[1])
        assert course_details.course_key == 'edX+E2E-101'
        assert course_details.course_type == 'verified-audit'
        assert course_details.product_source == 'edx'
        assert course_details.start_date.replace(tzinfo=None) == datetime.datetime(2022, 9, 11, 12, 1, 8)
        assert course_details.end_date is None
        assert course_details.enroll_by is None
