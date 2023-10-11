import pytest
from api.diagnostics_management import tasks
from bson import ObjectId
from celery import Celery


@pytest.fixture
def DiagnosticTaskManager():
    yield tasks.DiagnosticTaskManager
    # unset celery configuration after each test
    tasks.DiagnosticTaskManager.set_celery(None)


class TestDiagnosticTaskManager:

    def test_set_celery(self, DiagnosticTaskManager):
        DiagnosticTaskManager.set_celery(Celery())
        DiagnosticTaskManager()

    def test_init_fails_without_celery(self, DiagnosticTaskManager):
        with pytest.raises(AttributeError):
            DiagnosticTaskManager()

    @pytest.mark.asyncio
    async def test_call(
            self,
            DiagnosticTaskManager,
            monkeypatch
    ):
        DiagnosticTaskManager.set_celery(Celery())
        send_task_args = []

        def mock_send_task(self, name, args):
            send_task_args.append(name)
            send_task_args.append(args)

        monkeypatch.setattr(Celery, "send_task", mock_send_task)

        diag_id = ObjectId()
        await DiagnosticTaskManager()(diag_id)

        # confirm expected call to Celery.send_task
        assert send_task_args[0] == \
               DiagnosticTaskManager._diagnostic_task_name
        assert send_task_args[1] == (str(diag_id),)

    def test_get_vehicle_components(self, DiagnosticTaskManager, monkeypatch):
        DiagnosticTaskManager.set_celery(Celery())
        diagnostic_task_manager = DiagnosticTaskManager()

        test_components = ["comp 1", "comp 2"]

        class MockTask:
            @property
            def status(self):
                return "SUCCESS"

            def ready(self):
                return True

            def get(self):
                return test_components

        def mock_send_task(self, name):
            return MockTask()

        monkeypatch.setattr(Celery, "send_task", mock_send_task)

        retrieved_components = diagnostic_task_manager.get_vehicle_components()
        assert retrieved_components == test_components

    def test_get_vehicle_components_failed_task(
            self, DiagnosticTaskManager, monkeypatch
    ):
        DiagnosticTaskManager.set_celery(Celery())
        diagnostic_task_manager = DiagnosticTaskManager()

        class MockTask:
            @property
            def status(self):
                return "FAILED"

            def ready(self):
                return True

        def mock_send_task(self, name):
            return MockTask()

        monkeypatch.setattr(Celery, "send_task", mock_send_task)

        retrieved_components = diagnostic_task_manager.get_vehicle_components()
        assert retrieved_components == []

    def test_get_vehicle_components_timed_out(
            self, DiagnosticTaskManager, monkeypatch
    ):
        DiagnosticTaskManager.set_celery(Celery())
        diagnostic_task_manager = DiagnosticTaskManager()

        class MockTask:
            @property
            def status(self):
                return "PENDING"

            def ready(self):
                return False

        def mock_send_task(self, name):
            return MockTask()

        monkeypatch.setattr(Celery, "send_task", mock_send_task)

        retrieved_components = diagnostic_task_manager.get_vehicle_components()
        assert retrieved_components == []
