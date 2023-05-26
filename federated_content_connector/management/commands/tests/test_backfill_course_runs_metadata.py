"""
Tests for `backfill_course_runs_metadata` management command.
"""

from unittest import TestCase, mock
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from federated_content_connector.management.commands import backfill_course_runs_metadata
from federated_content_connector.models import CourseDetails


@pytest.mark.django_db
class TestBackfillCourserunsMetadataCommand(TestCase):
    """
    Tests `backfill_course_runs_metadata` management command.
    """

    def setUp(self):
        super().setUp()
        self.command = backfill_course_runs_metadata.Command()

    def test_command(self):
        assert False
