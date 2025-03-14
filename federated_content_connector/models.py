"""
Database models for federated_content_connector.
"""
from django.db import models
from django_extensions.db.models import TimeStampedModel
from opaque_keys.edx.django.models import CourseKeyField


class CourseDetails(TimeStampedModel):
    """
    Model to store Course metadata.

    .. no_pii:
    """

    id = CourseKeyField(
        db_index=True,
        primary_key=True,
        max_length=255,
        help_text='Courserun key'
    )

    course_key = models.CharField(
        max_length=255,
        help_text="The top-level course key associated with the course run key",
        blank=True,
        default=""
    )
    external_identifier = models.CharField(
        max_length=255,
        help_text="The identifier of the course in the external system",
        blank=True,
        default=""
    )
    course_type = models.CharField(
        max_length=255,
        help_text='Type of course. For example Masters, Verified, Audit, executive-education-2u,  etc'
    )
    product_source = models.CharField(
        max_length=255,
        help_text='Tells about the origin of a course. For example, edx, 2u'
    )
    start_date = models.DateTimeField(
        null=True,
        help_text='The start date of the course.'
    )
    end_date = models.DateTimeField(
        null=True,
        help_text='The end date of the course.'
    )
    enroll_by = models.DateTimeField(
        null=True,
        help_text='The suggested deadline for enrollment.'
    )

    class Meta:
        """
        Meta class for CourseDetails.
        """

        app_label = 'federated_content_connector'


class CourseDetailsImportStatus(TimeStampedModel):
    """
    CourseDetails import status history.

    .. no_pii:
    """

    TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

    last_successful_import_at = models.DateTimeField(help_text='Timestamp of last data import')

    @classmethod
    def last_successful_import_timestamp(cls):
        """
        Return `last_successful_import_at`.
        """
        last_import = cls.objects.first()
        if last_import:
            return last_import.last_successful_import_at.strftime(cls.TIMESTAMP_FORMAT)

        return None

    @classmethod
    def save_last_successful_import_timestamp(cls, timestamp):
        """
        Save `last_successful_import_at`.
        """
        last_import = cls.objects.first()
        if last_import:
            last_import.last_successful_import_at = timestamp
            last_import.save()
        else:
            cls.objects.create(last_successful_import_at=timestamp)

    class Meta:
        """
        Meta class for CourseDetailsImportStatus.
        """

        app_label = 'federated_content_connector'
