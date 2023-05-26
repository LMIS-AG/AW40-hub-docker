import httpx
from celery import Celery
from .hub_client import HubClient
from .interfaces import HubDataAccessor

# configuration
REDIS_HOST = "redis"
HUB_URL = "http://api:8000/v1"

# configuration is resolved
redis_uri = f"redis://{REDIS_HOST}:6379"
app = Celery("tasks", broker=redis_uri, backend=redis_uri)
app.conf.update(timezone="UTC")


@app.task
def diagnose(diag_id):

    hub_client = HubClient(
        hub_url=HUB_URL,
        diag_id=diag_id
    )

    data_accessor = HubDataAccessor(
        hub_client=hub_client
    )

    # STATE: Retrieve workshop info
    workshop_info = data_accessor.get_workshop_info()

    # STATE: Retrieve obd data
    obd_data = data_accessor.get_obd_data()
    if obd_data is None:
        hub_client.require_obd_data()
        return "Requested OBD data."
    hub_client.unrequire_obd_data()

    # STATE: Retrieve oscillogram for component 'Batterie'
    oscillogram = data_accessor.get_oscillograms_by_components(["Batterie"])[0]
    if oscillogram is None:
        hub_client.require_oscillogram("Batterie")
        return "Requested Oscillogram data"
    hub_client.unrequire_oscillogram("Batterie")

    return "Finished"
