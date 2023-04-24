from enum import Enum
from typing import List, Union

from pydantic import BaseModel

from .vehicle import Component


class DiagnosisStatus(str, Enum):
    action_required = "action_required"
    processing = "processing"
    finished = "finished"


class DataType(str, Enum):
    timeseries_data = "timeseries_data"
    obd_data = "obd_data"
    # symptoms = "symptoms"


class ActionType(str, Enum):
    add_data = "add_data"
    # select_data = "select_data"


class ActionStatus(str, Enum):
    open = "open"
    done = "done"


class RequiredAction(BaseModel):
    action_type: ActionType
    data_type: DataType
    component: Union[Component, None]
    action_status: ActionStatus = ActionStatus.open


class RequiredActionUpdate(BaseModel):
    action_status: ActionStatus


class Diagnosis(BaseModel):
    status: DiagnosisStatus
    required_actions: List[RequiredAction] = []

    process_data: dict = {}
