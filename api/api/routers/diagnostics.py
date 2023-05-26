from typing import List

from bson import ObjectId
from fastapi import APIRouter, HTTPException

from ..data_management import (
    Case,
    Diagnosis,
    DiagnosisDB,
    OBDData,
    Vehicle,
    Component,
    ToDo,
    Action
)

tags_metadata = [
    {
        "name": "Diagnostics",
        "description": "Endpoints for the AI based diagnostics backend"
    }
]


router = APIRouter(tags=["Diagnostics"])


@router.get(
    "/{diag_id}",
    status_code=200,
    response_model=Diagnosis
)
async def get_diagnosis(diag_id: str):
    """Get data of a diagnosis."""
    diag_db = await DiagnosisDB.get(diag_id)
    diag = await diag_db.to_diagnosis()
    return diag


@router.get(
    "/{diag_id}/obd_data",
    status_code=200,
    response_model=List[OBDData]
)
async def get_obd_data(diag_id: str):
    """Get OBD data for a diagnosis."""
    case = await Case.find_one({"diagnosis_id": ObjectId(diag_id)})
    return case.obd_data


@router.get(
    "/{diag_id}/vehicle",
    status_code=200,
    response_model=Vehicle
)
async def get_vehicle(diag_id: str):
    """Get vehicle data for a diagnosis."""
    case = await Case.find_one({"diagnosis_id": ObjectId(diag_id)})
    vehicle = await Vehicle.find_one({"vin": case.vehicle_vin})
    return vehicle


@router.get(
    "/{diag_id}/oscillograms",
    status_code=200,
    response_model=List[List[float]]
)
async def get_oscillograms(diag_id: str, component: Component):
    """Get all oscillograms for a specific component."""
    case = await Case.find_one({"diagnosis_id": ObjectId(diag_id)})
    signals = []
    for tsd in case.timeseries_data:
        if tsd.component == component:
            signals.append(
                await tsd.get_signal()
            )
    return signals


@router.post(
    "/{diag_id}/todos/{action_id}",
    status_code=201,
    response_model=ToDo
)
async def create_todo(diag_id: str, action_id: str):
    """Require a user action for a diagnosis."""
    diag = await DiagnosisDB.get(diag_id)
    action = await Action.get(action_id)
    if diag is None or action is None:
        raise HTTPException(404)
    # Requireing a user action is done by inserting a new entry for this
    # diagnosis-action pair in the todos collection
    todo = ToDo(diagnosis_id=diag_id, action_id=action_id)
    todo = await todo.create()
    return todo


@router.delete(
    "/{diag_id}/todos/{action_id}",
    status_code=200,
    response_model=None
)
async def delete_todo(diag_id: str, action_id: str):
    """Remove a required user action from a diagnosis."""
    diag = await DiagnosisDB.get(diag_id)
    action = await Action.get(action_id)
    if diag is None or action is None:
        raise HTTPException(404)
    todo = await ToDo.find_one(
        {"action_id": action_id, "diagnosis_id": ObjectId(diag_id)}
    )
    await todo.delete()
    return None
