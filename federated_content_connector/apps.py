"""
federated_content_connector Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings, PluginSignals


class FederatedContentConnectorConfig(AppConfig):
    """
    Configuration for the federated_content_connector Django application.
    """

    name = 'federated_content_connector'
    label = 'federated_content_connector'
    verbose_name = "Federated Content Connector"
    plugin_app = {
        PluginSettings.CONFIG: {
            'lms.djangoapp': {
                'common': {
                    PluginSettings.RELATIVE_PATH: 'settings.common',
                },
                'production': {
                    PluginSettings.RELATIVE_PATH: 'settings.production',
                },
            }
        },
        PluginSignals.CONFIG: {
            'lms.djangoapp': {
                PluginSignals.RECEIVERS: [
                    {
                        PluginSignals.SIGNAL_PATH: 'openedx.core.djangoapps.content.course_overviews.signals.IMPORT_COURSE_DETAILS',  # noqa: pylint: disable=line-too-long
                        PluginSignals.RECEIVER_FUNC_NAME: 'handle_courseoverview_import_course_details',
                    },
                    {
                        PluginSignals.SIGNAL_PATH: 'openedx.core.djangoapps.content.course_overviews.signals.DELETE_COURSE_DETAILS',  # noqa: pylint: disable=line-too-long
                        PluginSignals.RECEIVER_FUNC_NAME: 'handle_courseoverview_delete_course_details',
                    },
                ],
            }
        }
    }
