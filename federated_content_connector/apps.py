"""
federated_content_connector Django application initialization.
"""

from django.apps import AppConfig
from edx_django_utils.plugins.constants import PluginSettings


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
            }
        }
    }
