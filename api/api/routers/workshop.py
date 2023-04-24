from typing import List, Union

from bson import ObjectId
from bson.errors import InvalidId
from celery import Celery
from fastapi import APIRouter, HTTPException, Depends
from pydantic import NonNegativeInt

from ..data_management import (
    NewCase,
    Case,
    CaseUpdate,
    NewOBDData,
    OBDDataUpdate,
    OBDData,
    NewSymptom,
    Symptom,
    SymptomUpdate,
    TimeseriesDataUpdate,
    NewTimeseriesData,
    TimeseriesData,
    Vehicle,
    VehicleUpdate,
    Customer,
    Diagnosis,
    RequiredAction
)
from ..diagnostics_management import get_celery

tags_metadata = [
    {
        "name": "Workshop - Case Management",
        "description": "Manage cases and associated meta data of a workshop."
    },
    {
        "name": "Workshop - Data Management",
        "description": "Manage diagnostic data of a case."
    },
    {
        "name": "Workshop - Diagnostics",
        "description": "Manage diagnosis of a case."
    },
]


router = APIRouter()


@router.get(
    "/{workshop_id}/cases",
    status_code=200,
    response_model=List[Case],
    tags=["Workshop - Case Management"]
)
async def list_cases(
        workshop_id: str,
        customer_id: str = None,
        vin: str = None
) -> List[Case]:
    cases = await Case.find_in_hub(
        customer_id=customer_id, vin=vin, workshop_id=workshop_id
    )
    return cases


@router.post(
    "/{workshop_id}/cases",
    status_code=201,
    response_model=Case,
    tags=["Workshop - Case Management"]
)
async def add_case(workshop_id: str, case: NewCase) -> Case:
    case = Case(workshop_id=workshop_id, **case.dict())
    case = await case.insert()
    return case


async def case_from_workshop(workshop_id: str, case_id: str) -> Case:
    """
    Shared dependency for all endpoints with path root
    '/{workshop_id}/cases/{case_id}'. Returns the case with id {case_id} if it
     exists AND the respective case belongs to the workshop specified via
     {workshop_id}. Otherwise a 404 Not Found is raised.
    """

    no_case_with_id_exception = HTTPException(
            status_code=404,
            detail=f"No case with id '{case_id}' found "
                   f"for workshop '{workshop_id}'."
        )

    try:
        case_id = ObjectId(case_id)
    except InvalidId:
        # invalid id reports not found to user
        raise no_case_with_id_exception

    case = await Case.get(case_id)

    if case is None or case.workshop_id != workshop_id:
        # No case for THIS workshop
        raise no_case_with_id_exception
    else:
        return case


@router.get(
    "/{workshop_id}/cases/{case_id}",
    status_code=200,
    response_model=Case,
    tags=["Workshop - Case Management"]
)
async def get_case(case: Case = Depends(case_from_workshop)) -> Case:
    return case


@router.put(
    "/{workshop_id}/cases/{case_id}",
    status_code=200,
    tags=["Workshop - Case Management"]
)
async def update_case(
        update: CaseUpdate, case: Case = Depends(case_from_workshop)
):
    await case.set(update.dict(exclude_unset=True))
    return case


@router.delete(
    "/{workshop_id}/cases/{case_id}",
    status_code=200,
    response_model=None,
    tags=["Workshop - Case Management"]
)
async def delete_case(case: Case = Depends(case_from_workshop)):
    await case.delete()


@router.get(
    "/{workshop_id}/cases/{case_id}/customer",
    status_code=200,
    response_model=Customer, tags=["Workshop - Case Management"]
)
async def get_customer(case: Case = Depends(case_from_workshop)):
    customer = await Customer.get(case.customer_id)
    return customer


@router.get(
    "/{workshop_id}/cases/{case_id}/vehicle",
    status_code=200,
    response_model=Vehicle, tags=["Workshop - Case Management"]
)
async def get_vehicle(case: Case = Depends(case_from_workshop)):
    vehicle = await Vehicle.find_one({"vin": case.vehicle_vin})
    return vehicle


@router.put(
    "/{workshop_id}/cases/{case_id}/vehicle",
    status_code=200,
    response_model=Vehicle, tags=["Workshop - Case Management"]
)
async def update_vehicle(
        update: VehicleUpdate, case: Case = Depends(case_from_workshop)
):
    vehicle = await Vehicle.find_one({"vin": case.vehicle_vin})
    await vehicle.set(update.dict(exclude_unset=True))
    return vehicle


@router.get(
    "/{workshop_id}/cases/{case_id}/timeseries_data",
    status_code=200,
    response_model=List[TimeseriesData], tags=["Workshop - Data Management"]
)
def list_timeseries_data(case: Case = Depends(case_from_workshop)):
    """List all available timeseries datasets for a case."""
    return case.timeseries_data


@router.post(
    "/{workshop_id}/cases/{case_id}/timeseries_data",
    status_code=201,
    response_model=Case, tags=["Workshop - Data Management"]
)
async def add_timeseries_data(
        timeseries_data: NewTimeseriesData,
        case: Case = Depends(case_from_workshop),
        celery: Celery = Depends(get_celery)
) -> Case:
    """Add a new timeseries dataset to a case."""
    case = await case.add_timeseries_data(timeseries_data)
    if case.diag:
        case.diag.status = "processing"
        await case.save()
        celery.send_task("tasks.diagnose", (str(case.id),))
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}",
    status_code=200,
    tags=["Workshop - Data Management"]
)
async def get_timeseries_data(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> TimeseriesData:
    """Get a specific timeseries dataset from a case."""
    timeseries_data = case.get_timeseries_data(data_id)
    if timeseries_data is not None:
        return timeseries_data
    else:
        exception_detail = f"No timeseries_data with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_timeseries_data}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.get(
    "/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}/signal",
    status_code=200,
    tags=["Workshop - Data Management"])
async def get_timeseries_data_signal(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> TimeseriesData:
    """Get the signal of a specific timeseries dataset from a case."""
    timeseries_data = case.get_timeseries_data(data_id)
    if timeseries_data is not None:
        return await timeseries_data.get_signal()
    else:
        exception_detail = f"No timeseries_data with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_timeseries_data}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.put(
    "/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}",
    status_code=200,
    response_model=TimeseriesData, tags=["Workshop - Data Management"]
)
async def update_timeseries_data(
        data_id: NonNegativeInt,
        update: TimeseriesDataUpdate,
        case: Case = Depends(case_from_workshop)
):
    """Update a specific timeseries dataset of a case."""
    timeseries_data = await case.update_timeseries_data(
        data_id=data_id, update=update
    )
    if timeseries_data is not None:
        return timeseries_data
    else:
        exception_detail = f"No timeseries_data with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_timeseries_data}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.delete(
    "/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}",
    status_code=200,
    response_model=Case, tags=["Workshop - Data Management"]
)
async def delete_timeseries_data(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
):
    """Delete a specific timeseries dataset from a case."""
    await case.delete_timeseries_data(data_id)
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/obd_data",
    status_code=200,
    response_model=List[OBDData], tags=["Workshop - Data Management"]
)
async def list_obd_data(
        case: Case = Depends(case_from_workshop)
) -> List[OBDData]:
    """List all available obd datasets for a case."""
    return case.obd_data


@router.post(
    "/{workshop_id}/cases/{case_id}/obd_data",
    status_code=201,
    response_model=Case, tags=["Workshop - Data Management"]
)
async def add_obd_data(
        obd_data: NewOBDData,
        case: Case = Depends(case_from_workshop),
        celery: Celery = Depends(get_celery)
) -> Case:
    """Add a new obd dataset to a case."""
    case = await case.add_obd_data(obd_data)
    if case.diag:
        case.diag.status = "processing"
        await case.save()
        celery.send_task("tasks.diagnose", (str(case.id),))
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/obd_data/{data_id}",
    status_code=200,
    response_model=OBDData, tags=["Workshop - Data Management"]
)
async def get_obd_data(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> OBDData:
    """Get a specific obd dataset from a case."""
    obd_data = case.get_obd_data(data_id)
    if obd_data is not None:
        return obd_data
    else:
        exception_detail = f"No obd_data with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_obd_data}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.put(
    "/{workshop_id}/cases/{case_id}/obd_data/{data_id}",
    status_code=200,
    response_model=OBDData, tags=["Workshop - Data Management"]
)
async def update_obd_data(
        data_id: NonNegativeInt,
        update: OBDDataUpdate,
        case: Case = Depends(case_from_workshop)
):
    """Update a specific obd dataset from a case."""
    obd_data = await case.update_obd_data(data_id=data_id, update=update)
    if obd_data is not None:
        return obd_data
    else:
        exception_detail = f"No obd_data with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_obd_data}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.delete(
    "/{workshop_id}/cases/{case_id}/obd_data/{data_id}",
    status_code=200,
    response_model=Case, tags=["Workshop - Data Management"]
)
async def delete_obd_data(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> Case:
    """Delete a specific obd dataset from a case."""
    await case.delete_obd_data(data_id)
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/symptoms",
    status_code=200,
    response_model=List[Symptom], tags=["Workshop - Data Management"]
)
async def list_symptoms(
        case: Case = Depends(case_from_workshop)
) -> List[Symptom]:
    """List all available symptoms for a case."""
    return case.symptoms


@router.post(
    "/{workshop_id}/cases/{case_id}/symptoms",
    status_code=201,
    response_model=Case, tags=["Workshop - Data Management"]
)
async def add_symptom(
        symptom: NewSymptom, case: Case = Depends(case_from_workshop)
) -> Case:
    """Add a new symptom to a case."""
    case = await case.add_symptom(symptom)
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/symptoms/{data_id}",
    status_code=200,
    response_model=Symptom, tags=["Workshop - Data Management"]
)
async def get_symptom(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> Symptom:
    """Get a specific symptom from a case."""
    symptom = case.get_symptom(data_id)
    if symptom is not None:
        return symptom
    else:
        exception_detail = f"No symptom with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_symptoms}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.put(
    "/{workshop_id}/cases/{case_id}/symptoms/{data_id}",
    status_code=200,
    response_model=Symptom, tags=["Workshop - Data Management"]
)
async def update_symptom(
        data_id: NonNegativeInt,
        update: SymptomUpdate,
        case: Case = Depends(case_from_workshop)
):
    """Update a specific symptom of a case."""
    symptom = await case.update_symptom(data_id=data_id, update=update)
    if symptom is not None:
        return symptom
    else:
        exception_detail = f"No symptom with data_id `{data_id}` in " \
                           f"case '{case.id}'. Available data_ids are " \
                           f"{case.available_symptoms}."
        raise HTTPException(status_code=404, detail=exception_detail)


@router.delete(
    "/{workshop_id}/cases/{case_id}/symptoms/{data_id}",
    status_code=200,
    response_model=Case, tags=["Workshop - Data Management"]
)
async def delete_symptom(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> Case:
    """Delete a specific symptom from a case."""
    await case.delete_symptom(data_id)
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/diag",
    status_code=200,
    response_model=Union[Diagnosis, None],
    tags=["Workshop - Diagnostics"]
)
async def get_diagnosis(case: Case = Depends(case_from_workshop)):
    return case.diag


@router.post(
    "/{workshop_id}/cases/{case_id}/diag",
    status_code=201,
    response_model=Diagnosis,
    tags=["Workshop - Diagnostics"]
)
async def start_diagnosis(
        case: Case = Depends(case_from_workshop),
        celery: Celery = Depends(get_celery)
):
    if case.diag is not None:
        return case

    case.diag = Diagnosis(status="processing")
    await case.save()
    celery.send_task("tasks.diagnose", (str(case.id),))
    return case.diag


@router.put(
    "/{workshop_id}/cases/{case_id}/diag",
    status_code=200,
    response_model=Diagnosis,
    tags=["Workshop - Diagnostics"]
)
async def update_diagnosis(
        update: Diagnosis,
        case: Case = Depends(case_from_workshop)
):
    if case.diag is None:
        raise HTTPException(
            status_code=404,
            detail="No active diagnosis."
        )
    case.diag = update
    case = await case.save()
    return case.diag


@router.delete(
    "/{workshop_id}/cases/{case_id}/diag",
    status_code=200,
    response_model=None,
    tags=["Workshop - Diagnostics"]
)
async def delete_diagnosis(case: Case = Depends(case_from_workshop)):
    case.diag = None
    await case.save()
    return None


@router.get(
    "/{workshop_id}/cases/{case_id}/diag/required_actions",
    status_code=200,
    response_model=List[RequiredAction],
    tags=["Workshop - Diagnostics"]
)
async def get_required_actions(case: Case = Depends(case_from_workshop)):
    if case.diag is None:
        raise HTTPException(
            status_code=404,
            detail="No active diagnosis."
        )
    return case.diag.required_actions


@router.post(
    "/{workshop_id}/cases/{case_id}/diag/required_actions",
    status_code=201,
    response_model=Diagnosis,
    tags=["Workshop - Diagnostics"]
)
async def add_required_action(
        required_action: RequiredAction,
        case: Case = Depends(case_from_workshop)
):
    if case.diag is None:
        raise HTTPException(
            status_code=404,
            detail="No active diagnosis."
        )
    case.diag.required_actions.append(required_action)
    case.diag.status = "action_required"
    await case.save()
    return case.diag
