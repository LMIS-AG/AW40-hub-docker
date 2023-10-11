import time

from celery import Celery


class DiagnosticTaskManager:
    """
    Manages handing over tasks to the diagnostics service.
    """

    _celery: Celery = None
    _diagnostic_task_name: str = "diagnostics.tasks.diagnose"
    _get_vehicle_components_task_name: str = "diagnostics.tasks." \
                                             "get_vehicle_components"

    def __init__(self):
        if not self._celery:
            raise AttributeError("Celery not configured.")

    @classmethod
    def set_celery(cls, celery: Celery):
        cls._celery = celery

    async def __call__(self, diagnosis_id):
        """Send a diagnosis id to the diagnostics backend for processing."""
        self._celery.send_task(
            self._diagnostic_task_name, (str(diagnosis_id),)
        )

    def get_vehicle_components(self, timeout=0.5):
        """Get all vehicle components 'known' to the diagnostic backend."""
        task = self._celery.send_task(self._get_vehicle_components_task_name)
        start = time.time()
        while not task.ready() and (time.time() - start) < timeout:
            time.sleep(0.1)
        if task.status == "SUCCESS":
            return task.get()
        else:
            return []
