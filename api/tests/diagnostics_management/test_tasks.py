import pytest

from celery import Celery
from bson import ObjectId

from api.diagnostics_management import tasks
from api.data_management import DiagnosisDB


@pytest.fixture
def DiagnosticTaskManager():
    yield tasks.DiagnosticTaskManager
    tasks.DiagnosticTaskManager.set_celery(None)


@pytest.fixture
def manage_diagnostic_task(DiagnosticTaskManager):
    DiagnosticTaskManager.set_celery(Celery())
    yield DiagnosticTaskManager()


class TestDiagnosticTaskManager:

    def test_set_celery(self, DiagnosticTaskManager):
        DiagnosticTaskManager.set_celery(Celery())
        DiagnosticTaskManager()

    def test_init_fails_without_celery(self, DiagnosticTaskManager):
        with pytest.raises(AttributeError):
            DiagnosticTaskManager()

    @pytest.mark.asyncio
    async def test_call_no_diagnosis(self, manage_diagnostic_task):
        manage_diagnostic_task(None)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status", ["processing", "finished"])
    async def test_call_does_not_send_task(
            self,
            status,
            manage_diagnostic_task,
            initialized_beanie_context,
            monkeypatch
    ):
        def mock_send_task(*args, **kwargs):
            raise Exception("This function should not be called")

        monkeypatch.setattr(Celery, "send_task", mock_send_task)

        async with initialized_beanie_context:
            diag = await DiagnosisDB(
                **{"case_id": ObjectId(), "status": status}
            ).create()

            await manage_diagnostic_task(diag.id)

            # status should be unchanged
            diag = await DiagnosisDB.get(diag.id)
            assert diag.status == status

    @pytest.mark.asyncio
    async def test_call_does_send_task_for_status_action_required(
            self,
            manage_diagnostic_task,
            initialized_beanie_context,
            monkeypatch
    ):
        send_task_args = []

        def mock_send_task(self, name, args):
            send_task_args.append(name)
            send_task_args.append(args)

        monkeypatch.setattr(Celery, "send_task", mock_send_task)
        diag_id = ObjectId()

        async with initialized_beanie_context:
            # create diagnosis with status action_required
            diag = await DiagnosisDB(
                **{
                    "id": diag_id,
                    "case_id": ObjectId(),
                    "status": "action_required"
                }
            ).create()

            await manage_diagnostic_task(diag.id)

            # status should be 'processing' now
            diag = await DiagnosisDB.get(diag_id)
            assert diag.status == "processing"

            # confirm expected call to Celery.send_task
            assert send_task_args[0] == \
                   manage_diagnostic_task._diagnostic_task_name
            assert send_task_args[1][0] == str(diag_id)

    @pytest.mark.asyncio
    async def test_call_does_send_task_for_new_diag(
            self,
            manage_diagnostic_task,
            initialized_beanie_context,
            monkeypatch
    ):
        send_task_args = []

        def mock_send_task(self, name, args):
            send_task_args.append(name)
            send_task_args.append(args)

        monkeypatch.setattr(Celery, "send_task", mock_send_task)
        diag_id = ObjectId()

        async with initialized_beanie_context:
            # Create "new" diagnosis, e.g. one without a status
            diag = await DiagnosisDB(
                **{
                    "id": diag_id,
                    "case_id": ObjectId()
                }
            ).create()

            await manage_diagnostic_task(diag.id)

            # status should be 'processing' now
            diag = await DiagnosisDB.get(diag_id)
            assert diag.status == "processing"

            # confirm expected call to Celery.send_task
            assert send_task_args[0] == \
                   manage_diagnostic_task._diagnostic_task_name
            assert send_task_args[1][0] == str(diag_id)
