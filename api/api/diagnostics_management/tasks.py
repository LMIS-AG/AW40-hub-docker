from celery import Celery


class DiagnosticTaskSender:
    celery: Celery

    def __call__(self, diagnosis_id):
        self.celery.send_task(
            "diagnostics.tasks.diagnose", (str(diagnosis_id),)
        )
