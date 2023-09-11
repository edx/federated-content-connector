"""
Tests for `refresh_course_runs_metadata` management command.
"""
import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from django.core.management import call_command
from opaque_keys.edx.keys import CourseKey

from federated_content_connector.management.commands import refresh_course_runs_metadata
from federated_content_connector.management.commands.import_course_runs_metadata import CourseMetadataImporter
from federated_content_connector.management.commands.tests.test_utils import COURSES_ENDPOINT_RESPONSE, REFRESH_RESPONSE
from federated_content_connector.models import CourseDetails, CourseDetailsImportStatus


class MockResponse:
    """
    Mock API response class.
    """
    def __init__(self, status_code=200, response_type='import'):
        self.status_code = status_code
        self.response_type = response_type

    def raise_for_status(self):
        return True

    def json(self):
        """
        Return mocked json response.
        """
        if self.response_type == 'import':
            return COURSES_ENDPOINT_RESPONSE
        if self.response_type == 'refresh':
            return REFRESH_RESPONSE

        return COURSES_ENDPOINT_RESPONSE


@pytest.mark.django_db
class TestRefreshCourserunsMetadataCommand(TestCase):
    """
    Tests `refresh_course_runs_metadata` management command.
    """

    def setUp(self):
        super().setUp()
        self.command = refresh_course_runs_metadata.Command()

    def courserun_locators(self):
        """
        Return list of course locators.
        """
        return [
            CourseKey.from_string("course-v1:edX+DemoX+Demo_Course"),
            CourseKey.from_string("course-v1:edX+E2E-101+course"),
        ]

    @patch.object(CourseMetadataImporter, 'get_api_client')
    def test_command(self, mocked_get_api_client):
        """
        Verify that command work as expected.
        """
        assert CourseDetails.objects.count() == 0

        mocked_get_api_client.return_value = MagicMock()
        mocked_get_api_client.return_value.get = MagicMock(return_value=MockResponse(response_type='refresh'))

        CourseDetails.objects.create(
            id=self.courserun_locators()[0],
            course_type='executive-education-2u',
            product_source='2u',
            start_date=datetime.datetime(2023, 6, 19, 0, 0, 0),
            end_date=datetime.datetime(2023, 8, 11, 23, 59, 59),
            enroll_by=datetime.datetime(2023, 6, 13, 23, 59, 59),
        )
        CourseDetails.objects.create(
            id=self.courserun_locators()[1],
            course_type='verified-audit',
            product_source='edx',
            start_date=datetime.datetime(2022, 9, 11, 12, 1, 8),
            end_date=None,
            enroll_by=None,
        )

        assert CourseDetails.objects.count() == 2

        # Now refresh and then verify the data
        call_command(self.command)

        assert CourseDetails.objects.count() == 2

        course_details = CourseDetails.objects.get(id=self.courserun_locators()[0])
        assert course_details.course_type == 'no-id-professional'
        assert course_details.product_source == 'edx'
        assert course_details.start_date.replace(tzinfo=None) == datetime.datetime(2024, 3, 14, 0, 0, 0)
        assert course_details.end_date.replace(tzinfo=None) == datetime.datetime(2024, 5, 27, 23, 59, 59)
        assert course_details.enroll_by.replace(tzinfo=None) == datetime.datetime(2024, 6, 6, 0, 0, 0)

        course_details = CourseDetails.objects.get(id=self.courserun_locators()[1])
        assert course_details.course_type == 'professional'
        assert course_details.product_source == 'max'
        assert course_details.start_date.replace(tzinfo=None) == datetime.datetime(2024, 9, 11, 12, 1, 8)
        assert course_details.end_date is None
        assert course_details.enroll_by.replace(tzinfo=None) == datetime.datetime(2024, 9, 11, 12, 1, 8)

        assert CourseDetailsImportStatus.last_successful_import_timestamp() == '2024-12-12T13:03:44.184967Z'
