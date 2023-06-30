from celery import Celery

from ..data_management import DiagnosisStatus, DiagnosisDB


class DiagnosticTaskManager:
    """
    Manages handing over tasks to the diagnostics service, depending on the
    state of the current diagnosis state in the database
    """

    _celery: Celery = None
    _diagnostic_task_name: str = "diagnostics.tasks.diagnose"

    def __init__(self):
        if not self._celery:
            raise AttributeError("Celery not configured.")

    @classmethod
    def set_celery(cls, celery: Celery):
        cls._celery = celery

    async def __call__(self, diagnosis_id):
        if diagnosis_id:
            diag = await DiagnosisDB.get(diagnosis_id)
            if diag.status is None or \
                    diag.status == DiagnosisStatus.action_required:
                # Last status indicates a fresh diagnosis or that a user action
                # was required. Change status to processing and hand the
                # diagnosis over to the diagnostics service for consideration.
                diag.status = DiagnosisStatus.processing
                await diag.save()
                self._celery.send_task(
                    self._diagnostic_task_name, (str(diagnosis_id),)
                )

            # In other cases (diagnosis is already 'processing' or 'finished'),
            # there is no need to inform the diagnostics service
