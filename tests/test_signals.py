"""
Tests for the `federated_content_connector` signals module.
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

import pytest
from opaque_keys.edx.keys import CourseKey

from federated_content_connector.management.commands.import_course_runs_metadata import CourseMetadataImporter
from federated_content_connector.management.commands.tests.test_utils import side_effect_func
from federated_content_connector.models import CourseDetails
from federated_content_connector.signals import (
    handle_courseoverview_delete_course_details,
    handle_courseoverview_import_course_details,
)


@pytest.mark.django_db
class TestSignals(TestCase):
    """
    Tests class for signals.
    """

    def setUp(self):
        super().setUp()

        self.courserun_locators = [
            CourseKey.from_string("course-v1:edX+DemoX+Demo_Course"),
            CourseKey.from_string("course-v1:edX+E2E-101+course"),
        ]

    @patch.object(CourseMetadataImporter, 'get_api_client')
    @patch.object(CourseMetadataImporter, 'courserun_locators_to_import')
    def test_handle_courseoverview_import_course_details(self, mocked_courserun_locator, mocked_get_api_client):
        """
        Verify that `handle_courseoverview_import_course_details` signal handler work as expected.
        """
        # Mock api client and api responses
        mocked_get_api_client.return_value = MagicMock()
        mocked_get_api_client.return_value.get = MagicMock(side_effect=side_effect_func)
        mocked_courserun_locator.return_value = [self.courserun_locators[1]]

        assert CourseDetails.objects.count() == 0

        handle_courseoverview_import_course_details(None, str(self.courserun_locators[1]))

        assert CourseDetails.objects.count() == 1
        assert CourseDetails.objects.filter(id=self.courserun_locators[0]).exists() is False
        assert CourseDetails.objects.filter(id=self.courserun_locators[1]).exists()

    @patch.object(CourseMetadataImporter, 'get_api_client')
    @patch.object(CourseMetadataImporter, 'courserun_locators_to_import')
    def test_handle_courseoverview_delete_course_details(self, mocked_courserun_locator, mocked_get_api_client):
        """
        Verify that `handle_courseoverview_delete_course_details` signal handler work as expected.
        """
        # Mock api client and api responses
        mocked_get_api_client.return_value = MagicMock()
        mocked_get_api_client.return_value.get = MagicMock(side_effect=side_effect_func)
        mocked_courserun_locator.return_value = self.courserun_locators

        # Import data
        CourseMetadataImporter.import_all_courses_metadata()

        assert CourseDetails.objects.count() == 2

        handle_courseoverview_delete_course_details(None, self.courserun_locators[0])

        assert CourseDetails.objects.count() == 1
        assert CourseDetails.objects.filter(id=self.courserun_locators[0]).exists() is False
        assert CourseDetails.objects.filter(id=self.courserun_locators[1]).exists()
