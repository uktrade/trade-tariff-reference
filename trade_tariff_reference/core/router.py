from django.conf import settings


class Router:
    """
    A router to control all database operations on models in the tariff application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to the tariff db.
        """
        if model._meta.app_label == 'tariff':
            return 'tariff'
        return ''

    def db_for_write(self, model, **hints):
        """
        Attempts to write to the tariff application raises an exception as db is readonly.
        """
        if model._meta.app_label != 'tariff':
            return ''

        if settings.MANAGE_TARIFF_DATABASE:
            return 'tariff'
        raise Exception("This data is readonly")


    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        return None
