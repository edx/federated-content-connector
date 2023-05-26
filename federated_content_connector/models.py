"""
Database models for federated_content_connector.
"""
from django.db import models
from opaque_keys.edx.django.models import CourseKeyField
from django_extensions.db.models import TimeStampedModel


class CourseDetails(TimeStampedModel):

    id = CourseKeyField(db_index=True, primary_key=True, max_length=255)

    course_type = models.CharField(
        max_length=255,
        help_text='Type of course. For example "Masters, Verified, Audit", "Verified and Audit" etc'
    )
    product_source = models.CharField(
        max_length=255,
        help_text='Tells about the origin of a course. For example, ???'
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
        app_label = 'federated_content_connector'

