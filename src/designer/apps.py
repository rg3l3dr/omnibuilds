from __future__ import unicode_literals
from django.apps import AppConfig


class DesignerConfig(AppConfig):
    name = 'designer'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('UserProfile'))
