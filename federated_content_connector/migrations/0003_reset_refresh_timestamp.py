
from django.db import migrations


def remove_last_refresh_timestamp(apps, schema_editor):
    course_details_import_status = apps.get_model('federated_content_connector', 'CourseDetailsImportStatus')
    course_details_import_status.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('federated_content_connector', '0002_coursedetailsimportstatus'),
    ]

    operations = [
        migrations.RunPython(
            code=remove_last_refresh_timestamp,
            reverse_code=None
        )

    ]
