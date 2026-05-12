from django.apps import AppConfig


class AssertsManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'asserts_manager'

    def ready(self):
        import asserts_manager.signals  # 注册信号
