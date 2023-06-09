# Generated by Django 3.2.19 on 2023-06-16 12:12

from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('federated_content_connector', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseDetailsImportStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('last_successful_import_at', models.DateTimeField(help_text='Timestamp of last data import')),
            ],
        ),
    ]
