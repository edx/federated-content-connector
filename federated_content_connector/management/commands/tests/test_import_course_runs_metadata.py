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
from federated_content_connector.management.commands.tests.mock_responses import COURSES_ENDPOINT_RESPONSE
from federated_content_connector.models import CourseDetails


class MockResponse:
    """
    Mock API response class.
    """
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        return True

    def json(self):
        return COURSES_ENDPOINT_RESPONSE


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
            CourseKey.from_string("course-v1:edX+DemoX+Demo_Course"),
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
        mocked_get_api_client.return_value.get = MagicMock(return_value=MockResponse())
        mocked_courserun_locators_to_import.return_value = self.courserun_locators()

        call_command(self.command)

        assert CourseDetails.objects.count() == 2

        course_details = CourseDetails.objects.get(id=self.courserun_locators()[0])
        assert course_details.course_type == 'executive-education-2u'
        assert course_details.product_source == '2u'
        assert course_details.start_date.replace(tzinfo=None) == datetime.datetime(2023, 1, 1, 17, 29, 21)
        assert course_details.end_date.replace(tzinfo=None) == datetime.datetime(2023, 8, 31, 17, 29, 25)
        assert course_details.enroll_by.replace(tzinfo=None) == datetime.datetime(2023, 5, 31, 17, 29, 42)

        course_details = CourseDetails.objects.get(id=self.courserun_locators()[1])
        assert course_details.course_type == 'verified-audit'
        assert course_details.product_source == ''
        assert course_details.start_date.replace(tzinfo=None) == datetime.datetime(2022, 9, 11, 12, 1, 8)
        assert course_details.end_date is None
        assert course_details.enroll_by is None
