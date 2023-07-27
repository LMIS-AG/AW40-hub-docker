import smach

from celery import Celery
from vehicle_diag_smach.data_types.state_transition import StateTransition
from vehicle_diag_smach.high_level_smach import VehicleDiagnosisStateMachine

from .hub_client import HubClient
from .interfaces import (
    HubDataAccessor,
    HubDataProvider,
    HubModelAccessor
)


# Make smach less verbose by disabling non-error logging
def dont_log(msg):
    pass


def log_err(msg):
    print("[ ERROR ] : " + str(msg))


smach.set_loggers(
    info=dont_log, warn=dont_log, debug=dont_log, error=log_err
)

# configuration
REDIS_HOST = "redis"
HUB_URL = "http://api:8000/v1"
DATA_POLL_INTERVAL = 1
MODELS_DIR = "models"
KG_URL = "http://knowledge-graph:3030"

# configuration is resolved
redis_uri = f"redis://{REDIS_HOST}:6379"
app = Celery("tasks", broker=redis_uri, backend=redis_uri)
app.conf.update(timezone="UTC")


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
        hub_client=hub_client,
        data_poll_interval=DATA_POLL_INTERVAL
    )
    data_provider = HubDataProvider(
        hub_client=hub_client
    )
    model_accessor = HubModelAccessor(models_dir=MODELS_DIR)

    # instantiate state machine
    sm = VehicleDiagnosisStateMachine(
        data_accessor=data_accessor,
        data_provider=data_provider,
        model_accessor=model_accessor,
        kg_url=KG_URL
    )

    # execute diagnosis
    hub_client.set_diagnosis_status("processing")
    sm.execute()
    hub_client.set_diagnosis_status("finished")
