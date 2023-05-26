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
    plugin_app = {
        PluginSettings.CONFIG: {
            'lms.djangoapp': {
                'common': {
                    PluginSettings.RELATIVE_PATH: 'settings.common',
                },
                'production': {
                    PluginSettings.RELATIVE_PATH: 'settings.production',
                },
                PluginSignals.RECEIVERS: [
                    {
                        PluginSignals.SIGNAL_PATH: 'openedx.core.djangoapps.content.course_overviews.signals.import_course_metadata',
                        PluginSignals.RECEIVER_FUNC_NAME: 'handle_courseoverview_import_course_metadata',
                    },
                    {
                        PluginSignals.SIGNAL_PATH: 'openedx.core.djangoapps.content.course_overviews.signals.delete_course_metadata',
                        PluginSignals.RECEIVER_FUNC_NAME: 'handle_courseoverview_delete_course_metadata',
                    },
                ],
            }
        }
    }
