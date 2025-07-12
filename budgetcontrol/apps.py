from django.apps import AppConfig

class BudgetcontrolConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'budgetcontrol'

    def ready(self) -> None:
        import budgetcontrol.signals