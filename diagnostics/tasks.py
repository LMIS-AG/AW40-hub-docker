import httpx
from celery import Celery

"""
Sketch of a 'diagnostic backend' that consumes data via the hub api and
uses a TensorFlow model server to evaluate oscilloscope signals.
"""

# configuration
REDIS_HOST = "redis"
API_URL = "http://api:8000/v1"
MODEL_SERVER_URL = "http://model-server:8501/v1/models"

# configuration is resolved
redis_uri = f"redis://{REDIS_HOST}:6379"
app = Celery("tasks", broker=redis_uri, backend=redis_uri)
app.conf.update(timezone="UTC")


def fetch_case(case_id: str):
    """Fetch case from Hub API via its id"""
    url = f"{API_URL}/shared/cases/{case_id}"
    response = httpx.get(url)
    assert response.status_code == 200
    return response.json()


def update_diag(case: dict):
    """Update existing diag of case via Hub API"""
    workshop_id = case["workshop_id"]
    case_id = case["_id"]
    url = f"{API_URL}/{workshop_id}/cases/{case_id}/diag"
    response = httpx.put(url, json=case["diag"])
    assert response.status_code == 200


def get_signal(case: str, data_id: int):
    """Fetch a specific signal via the Hub API"""
    workshop_id = case["workshop_id"]
    case_id = case["_id"]
    url = f"{API_URL}/{workshop_id}/cases/{case_id}/timeseries_data" \
          f"/{data_id}/signal"
    response = httpx.get(url)
    assert response.status_code == 200
    return response.json()


# components are mapped to model endpoints
component_models = {
    "Batterie": f"{MODEL_SERVER_URL}/model:predict"
}


def get_signal_prediction(case, data_id):
    # fetch signal via Hub API
    signal = get_signal(case, data_id)

    # use cataloge "component_models" to lookup the appropriate model endpoint
    component = case["timeseries_data"][data_id]["component"]
    url = component_models[component]

    # query the model server to get a prediction
    response = httpx.post(url, json={"inputs": [signal]})
    assert response.status_code == 200
    return response.json()["outputs"]


class State:
    """Demo State to process data from hub api"""

    def __init__(
            self, name,
            required_data_type=None,
            required_component=None,
            procfun=lambda case, data_id: None
    ):
        self.name = name
        self.required_data_type = required_data_type
        self.required_component = required_component
        self.procfun = procfun

        print(f"STATE: {self.name}")

    def create_required_action(self, status):
        return {
            "action_type": "add_data",
            "data_type": self.required_data_type,
            "component": self.required_component,
            "action_status": status
        }

    def find_requirement_action(self, case):
        required_actions = case["diag"]["required_actions"]
        for i, req in enumerate(required_actions):
            req_found = (req["action_type"] == "add_data")
            req_found &= (req["data_type"] == self.required_data_type)
            req_found &= (req["component"] == self.required_component)
            if req_found:
                return i

        return None

    def find_requirement_data_id(self, case):
        for d in case[self.required_data_type]:
            if d.get("component") == self.required_component:
                return d["data_id"]

        return None

    def _process_requirements(self, case):

        if self.required_data_type is None:
            return case, None

        requirement_data_id = self.find_requirement_data_id(case)
        if requirement_data_id is not None:
            case["diag"]["status"] = "processing"
            req = self.create_required_action(status="done")

        else:
            case["diag"]["status"] = "action_required"
            req = self.create_required_action(status="open")

        requirement_idx = self.find_requirement_action(case)
        if requirement_idx is None:
            case["diag"]["required_actions"].append(req)
        else:
            case["diag"]["required_actions"][requirement_idx] = req

        return case, requirement_data_id

    def process(self, case):
        finished = False
        result = None

        case, data_id = self._process_requirements(case)
        if data_id is not None:
            result = self.procfun(case, data_id)
            finished = True

        if not case["diag"]["process_data"].get("finished_states"):
            case["diag"]["process_data"]["finished_states"] = []

        if finished and self.name not in \
                case["diag"]["process_data"]["finished_states"]:
            case["diag"]["process_data"]["finished_states"].append(self.name)
        case["diag"]["process_data"]["last_state"] = self.name

        return case, finished, result


# initialize some demo states
states = [
    # State 1 waits for OBD Data
    State(
        "Require OBD Data",
        required_data_type="obd_data"
    ),
    # State 2 just logs "Process OBD Data"
    State(
        "Process OBD Data",
        required_data_type="obd_data"
    ),
    # State 3 waits for availability of timeseries data of Batterie
    State(
        "Require timeseries data for component 'Batterie'",
        required_data_type="timeseries_data",
        required_component="Batterie"
    ),
    # State 4 sends Batterie signal to tf model server
    State(
        "Process timeseries data",
        required_data_type="timeseries_data",
        required_component="Batterie",
        procfun=get_signal_prediction
    )
]


@app.task
def diagnose(case_id):
    # fetch case data via hub api
    case = fetch_case(case_id)

    for state in states:
        # state-specific processing of case
        case, finished, result = state.process(case)
        # use hub api to save current diagnosis state
        update_diag(case)
        if not finished:
            # if not finished (e.g. more data required) return and stop
            return case["diag"]

    # Save result and set diag status to finished
    case["diag"]["process_data"]["result"] = result
    case["diag"]["status"] = "finished"
    # use hub api to save current diagnosis state
    update_diag(case)
    return case["diag"]
