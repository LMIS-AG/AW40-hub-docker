from typing import List

from fastapi import APIRouter, HTTPException, Depends

from ..data_management import NewCase, Case, Component, OBDData, Symptom

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
        workshop_id: str = None,
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
    case = await Case.get(case_id)

    if case is None or case.workshop_id != workshop_id:
        # No case for THIS workshop
        raise HTTPException(
            status_code=404,
            detail=f"No case with id '{case_id}' found "
                   f"for workshop '{workshop_id}'."
        )
    else:
        return case


@router.get(
    "/{workshop_id}/cases/{case_id}", status_code=200, response_model=Case
)
async def get_case(case: Case = Depends(case_from_workshop)) -> Case:
    return case


@router.put("/{workshop_id}/cases/{case_id}")
def update_case(case: Case = Depends(case_from_workshop)):
    pass


@router.delete("/{workshop_id}/cases/{case_id}")
def delete_case(case: Case = Depends(case_from_workshop)):
    pass


@router.get("/{workshop_id}/cases/{case_id}/customer")
def get_customer(case: Case = Depends(case_from_workshop)):
    pass


@router.put("/{workshop_id}/cases/{case_id}/customer")
def update_customer(case: Case = Depends(case_from_workshop)):
    pass


@router.get("/{workshop_id}/cases/{case_id}/vehicle")
def get_vehicle(case: Case = Depends(case_from_workshop)):
    pass


@router.put("/{workshop_id}/cases/{case_id}/vehicle")
def update_vehicle(case: Case = Depends(case_from_workshop)):
    pass


@router.get("/{workshop_id}/cases/{case_id}/timeseries_data")
def list_timeseries_data(case: Case = Depends(case_from_workshop)):
    """List all available timeseries datasets for a case."""
    pass


@router.post("/{workshop_id}/cases/{case_id}/timeseries_data")
def add_timeseries_data(case: Case = Depends(case_from_workshop)):
    """Add a new timeseries dataset to a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
def get_timeseries_data(
        data_id: str, case: Case = Depends(case_from_workshop)
):
    """Get a specific timeseries dataset from a case."""
    pass


@router.put("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
def update_timeseries_data(
        data_id: str, case: Case = Depends(case_from_workshop)
):
    """Update a specific timeseries dataset of a case."""
    pass


@router.delete("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
def delete_timeseries_data(
        data_id: str, case: Case = Depends(case_from_workshop)
):
    """Delete a specific timeseries dataset from a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/obd_data")
def list_obd_data(case: Case = Depends(case_from_workshop)):
    """List all available obd datasets for a case."""
    pass


@router.post(
    "/{workshop_id}/cases/{case_id}/obd_data",
    status_code=201,
    response_model=Case
)
async def add_obd_data(
        obd_data: OBDData, case: Case = Depends(case_from_workshop),
) -> Case:
    """Add a new obd dataset to a case."""
    case.obd_data.append(obd_data)
    case = await case.save()
    return case


@router.get("/{workshop_id}/cases/{case_id}/obd_data/{data_id}")
def get_obd_data(data_id: str, case: Case = Depends(case_from_workshop)):
    """Get a specific obd dataset from a case."""
    pass


@router.put("/{workshop_id}/cases/{case_id}/obd_data/{data_id}")
def update_obd_data(data_id: str, case: Case = Depends(case_from_workshop)):
    """Update a specific obd dataset of a case."""
    pass


@router.delete("/{workshop_id}/cases/{case_id}/obd_data/{data_id}")
def delete_obd_data(data_id: str, case: Case = Depends(case_from_workshop)):
    """Delete a specific obd dataset from a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/symptoms")
def list_symptoms(case: Case = Depends(case_from_workshop)):
    pass


@router.post(
    "/{workshop_id}/cases/{case_id}/symptoms",
    status_code=201, response_model=Case
)
async def add_symptom(
        symptom: Symptom, case: Case = Depends(case_from_workshop)
) -> Case:
    """Add a new symptom to a case."""
    case.symptoms.append(symptom)
    case = await case.save()
    return case


@router.get("/{workshop_id}/cases/{case_id}/symptoms/{component}")
def get_symptom(
        component: Component, case: Case = Depends(case_from_workshop)
):
    pass


@router.put("/{workshop_id}/cases/{case_id}/symptoms/{component}")
def update_symptom(
        component: Component, case: Case = Depends(case_from_workshop)
):
    pass


@router.delete("/{workshop_id}/cases/{case_id}/symptoms/{component}")
def delete_symptom(
        component: Component, case: Case = Depends(case_from_workshop)
):
    pass
