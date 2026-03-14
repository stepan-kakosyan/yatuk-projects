from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poem'
    verbose_name = "Poem"
    verbose_name_plural = "Poems"
