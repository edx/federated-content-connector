"""Mocked Models"""

class CatalogIntegration:

    service_username = 'abc'

    @classmethod
    def current(cls, *args, **kwargs):
        return cls
