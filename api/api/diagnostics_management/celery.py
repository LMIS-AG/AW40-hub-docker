from celery import Celery


class GetCelery:

    broker: str
    backend: str

    def __call__(self):
        return Celery(broker=self.broker, backend=self.backend)


get_celery = GetCelery()
