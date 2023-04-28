from typing import List
from typing import Literal

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import NonNegativeInt, PositiveInt

from ..data_management import (
    NewCase,
    Case,
    CaseUpdate,
    Component,
    NewOBDData,
    OBDDataUpdate,
    OBDData,
    NewSymptom,
    Symptom,
    SymptomUpdate,
    TimeseriesDataUpdate,
    NewTimeseriesData,
    TimeseriesData,
    TimeseriesDataLabel,
    Vehicle,
    VehicleUpdate,
    Customer
)
from ..upload_filereader import filereader_factory

tags_metadata = [
    {
        "name": "Workshop",
        "description": "Manage cases and associated diagnostic data of a "
                       "workshop"
    }
]


router = APIRouter(tags=["Workshop"])


@router.get("/{workshop_id}/cases", status_code=200, response_model=List[Case])
async def list_cases(
        workshop_id: str,
        customer_id: str = None,
        vin: str = None
) -> List[Case]:
    cases = await Case.find_in_hub(
        customer_id=customer_id, vin=vin, workshop_id=workshop_id
    )
    return cases


@router.post("/{workshop_id}/cases", status_code=201, response_model=Case)
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
    "/{workshop_id}/cases/{case_id}", status_code=200, response_model=Case
)
async def get_case(case: Case = Depends(case_from_workshop)) -> Case:
    return case


@router.put("/{workshop_id}/cases/{case_id}")
async def update_case(
        update: CaseUpdate, case: Case = Depends(case_from_workshop)
):
    await case.set(update.dict(exclude_unset=True))
    return case


@router.delete(
    "/{workshop_id}/cases/{case_id}", status_code=200, response_model=None
)
async def delete_case(case: Case = Depends(case_from_workshop)):
    await case.delete()


@router.get(
    "/{workshop_id}/cases/{case_id}/customer",
    status_code=200,
    response_model=Customer
)
async def get_customer(case: Case = Depends(case_from_workshop)):
    customer = await Customer.get(case.customer_id)
    return customer


@router.get(
    "/{workshop_id}/cases/{case_id}/vehicle",
    status_code=200,
    response_model=Vehicle
)
async def get_vehicle(case: Case = Depends(case_from_workshop)):
    vehicle = await Vehicle.find_one({"vin": case.vehicle_vin})
    return vehicle


@router.put(
    "/{workshop_id}/cases/{case_id}/vehicle",
    status_code=200,
    response_model=Vehicle
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
    response_model=List[TimeseriesData]
)
def list_timeseries_data(case: Case = Depends(case_from_workshop)):
    """List all available timeseries datasets for a case."""
    return case.timeseries_data


@router.post(
    "/{workshop_id}/cases/{case_id}/timeseries_data",
    status_code=201,
    response_model=Case
)
async def add_timeseries_data(
        timeseries_data: NewTimeseriesData,
        case: Case = Depends(case_from_workshop)
) -> Case:
    """Add a new timeseries dataset to a case."""
    case = await case.add_timeseries_data(timeseries_data)
    return case


@router.post(
    "/{workshop_id}/cases/{case_id}/timeseries_data/upload/picoscope",
    status_code=201,
    response_model=Case
)
async def upload_picoscope_data(
        upload: UploadFile = File(),
        file_format: Literal["Picoscope MAT", "Picoscope CSV"] = Form(),
        component: Component = Form(),  # TODO: Or mapping channel->component
        label: TimeseriesDataLabel = Form(),  # TODO: Or mapping channel->label
        case: Case = Depends(case_from_workshop)

):
    reader = filereader_factory.get_reader(file_format)
    data = reader.read_file(upload.file)
    if len(data) > 1:
        raise HTTPException(
            status_code=422,
            detail="Multi Channel Upload is WIP"
        )
    # TODO: handle multi channel upload
    data = data[0]
    data["component"] = component
    data["label"] = label
    data["type"] = "oscillogram"
    case = await case.add_timeseries_data(
        NewTimeseriesData(**data)
    )
    return case


@router.post(
    "/{workshop_id}/cases/{case_id}/timeseries_data/upload/omniscope",
    status_code=201,
    response_model=Case
)
async def upload_omniscope_data(
        upload: UploadFile = File(),
        file_format: Literal["Omniscope V1 RAW"] = Form(),
        component: Component = Form(),
        label: TimeseriesDataLabel = Form(),
        sampling_rate: PositiveInt = Form(),
        case: Case = Depends(case_from_workshop)

):
    reader = filereader_factory.get_reader(file_format)
    data = reader.read_file(upload.file)
    if len(data) > 1:
        raise HTTPException(
            status_code=422,
            detail="Multi Channel Upload not allowed"
        )
    data = data[0]
    data["component"] = component
    data["label"] = label
    data["type"] = "oscillogram"
    data["sampling_rate"] = sampling_rate
    data["duration"] = len(data["signal"]) / sampling_rate
    case = await case.add_timeseries_data(
        NewTimeseriesData(**data)
    )
    return case


@router.get("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
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


@router.get("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}/signal")
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
    response_model=TimeseriesData
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
    response_model=Case
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
    response_model=List[OBDData]
)
async def list_obd_data(
        case: Case = Depends(case_from_workshop)
) -> List[OBDData]:
    """List all available obd datasets for a case."""
    return case.obd_data


@router.post(
    "/{workshop_id}/cases/{case_id}/obd_data",
    status_code=201,
    response_model=Case
)
async def add_obd_data(
        obd_data: NewOBDData, case: Case = Depends(case_from_workshop),
) -> Case:
    """Add a new obd dataset to a case."""
    case = await case.add_obd_data(obd_data)
    return case


@router.post(
    "/{workshop_id}/cases/{case_id}/obd_data/upload/vcds",
    status_code=201,
    response_model=Case
)
async def upload_vcds_data(
        upload: UploadFile = File(),
        file_format: Literal["VCDS TXT"] = Form(),
        case: Case = Depends(case_from_workshop)
):
    reader = filereader_factory.get_reader(file_format)
    data = reader.read_file(upload.file)
    if len(data) > 1:
        raise HTTPException(
            status_code=422,
            detail="Multi Channel Upload not allowed"
        )
    data = data[0]
    data = data["obd_data"]
    case = await case.add_obd_data(
        NewOBDData(**data)
    )
    return case


@router.get(
    "/{workshop_id}/cases/{case_id}/obd_data/{data_id}",
    status_code=200,
    response_model=OBDData
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
    response_model=OBDData
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
    response_model=Case
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
    response_model=List[Symptom]
)
async def list_symptoms(
        case: Case = Depends(case_from_workshop)
) -> List[Symptom]:
    """List all available symptoms for a case."""
    return case.symptoms


@router.post(
    "/{workshop_id}/cases/{case_id}/symptoms",
    status_code=201,
    response_model=Case
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
    response_model=Symptom
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
    response_model=Symptom
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
    response_model=Case
)
async def delete_symptom(
        data_id: NonNegativeInt, case: Case = Depends(case_from_workshop)
) -> Case:
    """Delete a specific symptom from a case."""
    await case.delete_symptom(data_id)
    return case
