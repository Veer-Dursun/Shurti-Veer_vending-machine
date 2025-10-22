from django.apps import AppConfig

class MachineConfig(AppConfig):
    name = 'machine'

    def ready(self):
        import machine.signals  # Register the signals file
