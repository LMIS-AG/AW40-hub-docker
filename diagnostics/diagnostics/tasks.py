from celery import Celery
from vehicle_diag_smach.data_types.state_transition import StateTransition

from .hub_client import HubClient
from .interfaces import (
    HubDataAccessor,
    HubDataProvider,
    HubModelAccessor,
    MissingOBDDataException,
    MissingOscillogramsException
)

# configuration
REDIS_HOST = "redis"
HUB_URL = "http://api:8000/v1"

# configuration is resolved
redis_uri = f"redis://{REDIS_HOST}:6379"
app = Celery("tasks", broker=redis_uri, backend=redis_uri)
app.conf.update(timezone="UTC")


def execute_smach(
        data_accessor: HubDataAccessor,
        data_provider: HubDataProvider,
        model_accessor: HubModelAccessor
):
    """Mocks execution of the actual state machine"""
    print(data_accessor.get_workshop_info())
    data_provider.provide_state_transition(
        StateTransition("GET_WORKSHOP_INFO", "GET_OBD_DATA", "LINK")
    )

    print(data_accessor.get_obd_data())
    data_provider.provide_state_transition(
        StateTransition("GET_OBD_DATA", "GET_OSCILLOGRAMS_DATA", "LINK")
    )

    print(data_accessor.get_oscillograms_by_components(["Batterie"]))
    data_provider.provide_state_transition(
        StateTransition("GET_OSCILLOGRAMS_DATA", "GET_MODEL", "LINK")
    )

    print(model_accessor.get_model_by_component("Batterie"))
    data_provider.provide_state_transition(
        StateTransition("GET_MODEL", "FINISH_DIAG", "LINK")
    )

    # TODO: provider functions for images

    print(
        data_provider.provide_diagnosis(
            ["fault-path-step-1", "fault-path-step-2"]
        )
    )


def refresh_todos(hub_client: HubClient):
    """Helper to check and refresh todos in a diagnosis."""
    todos = hub_client.get_todos()
    for todo in todos:
        todo_id = todo["_id"]
        if todo_id == "add-data-obd":
            if len(hub_client.get_obd_data()) > 0:
                # is done
                hub_client.unrequire_obd_data()
        elif "add-data-oscillogram" in todo_id:
            todo_component = todo["component"]
            if len(hub_client.get_oscillograms(todo_component)) > 0:
                # is done
                hub_client.unrequire_oscillogram(todo_component)
        else:
            raise ValueError(f"Unknown todo '{todo_id}'")

    # return remaining todos
    return hub_client.get_todos()


@app.task
def diagnose(diag_id):
    """Main task for a diagnosis."""

    # api client to interact with the specified diagnosis
    hub_client = HubClient(
        hub_url=HUB_URL,
        diag_id=diag_id
    )

    # set up vehicle_diag_smach interfaces
    data_accessor = HubDataAccessor(
        hub_client=hub_client
    )
    data_provider = HubDataProvider(
        hub_client=hub_client
    )
    model_accessor = HubModelAccessor()

    # before running the state machine, we refresh the diagnosis list of
    # required user actions
    remaining_todos = refresh_todos(hub_client)

    if remaining_todos == []:
        # No more user actions required. Flush log and (re)execute smach
        hub_client.clear_state_machine_log()
        try:
            execute_smach(
                data_accessor,
                data_provider,
                model_accessor
            )
            hub_client.set_diagnosis_status("finished")
        except MissingOBDDataException:
            hub_client.require_obd_data()
            hub_client.set_diagnosis_status("action_required")
        except MissingOscillogramsException as e:
            for component in e.components:
                hub_client.require_oscillogram(component)
            hub_client.set_diagnosis_status("action_required")

    else:
        hub_client.set_diagnosis_status("action_required")
