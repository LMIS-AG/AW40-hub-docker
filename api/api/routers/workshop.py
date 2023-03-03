from typing import List

from fastapi import APIRouter, HTTPException

from ..data_management import NewCase, Case, Component

tags_metadata = [
    {
        "name": "Workshop",
        "description": "Manage cases and associated diagnostic data of a "
                       "workshop"
    }
]


router = APIRouter(tags=["Workshop"])


class CaseNotFoundException(HTTPException):
    """Custom 404 for a specific (workshop_id, case_id) ressource."""
    def __init__(self, case_id, workshop_id):
        super().__init__(
            status_code=404,
            detail=f"No case with id '{case_id}' found "
                   f"for workshop '{workshop_id}'."
        )


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


@router.get(
    "/{workshop_id}/cases/{case_id}", status_code=200, response_model=Case
)
async def get_case(workshop_id: str, case_id: str) -> Case:
    case = await Case.get(case_id)

    if case is None or case.workshop_id != workshop_id:
        # No case for THIS workshop
        raise CaseNotFoundException(case_id=case_id, workshop_id=workshop_id)
    else:
        return case


@router.put("/{workshop_id}/cases/{case_id}")
def update_case(workshop_id: str, case_id: str):
    pass


@router.delete("/{workshop_id}/cases/{case_id}")
def delete_case(workshop_id: str, case_id: str):
    pass


@router.get("/{workshop_id}/cases/{case_id}/customer")
def get_customer(workshop_id: str, case_id: str):
    pass


@router.put("/{workshop_id}/cases/{case_id}/customer")
def update_customer(workshop_id: str, case_id: str):
    pass


@router.get("/{workshop_id}/cases/{case_id}/vehicle")
def get_vehicle(workshop_id: str, case_id: str):
    pass


@router.put("/{workshop_id}/cases/{case_id}/vehicle")
def update_vehicle(workshop_id: str, case_id: str):
    pass


@router.get("/{workshop_id}/cases/{case_id}/timeseries_data")
def list_timeseries_data(workshop_id: str, case_id: str):
    """List all available timeseries datasets for a case."""
    pass


@router.post("/{workshop_id}/cases/{case_id}/timeseries_data")
def add_timeseries_data(workshop_id: str, case_id: str, timeseries_data: None):
    """Add a new timeseries dataset to a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
def get_timeseries_data(workshop_id: str, case_id: str, data_id: str):
    """Get a specific timeseries dataset from a case."""
    pass


@router.put("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
def update_timeseries_data(workshop_id: str, case_id: str, data_id: str):
    """Update a specific timeseries dataset of a case."""
    pass


@router.delete("/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}")
def delete_timeseries_data(workshop_id: str, case_id: str, data_id: str):
    """Delete a specific timeseries dataset from a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/obd_data")
def list_obd_data(workshop_id: str, case_id: str):
    """List all available obd datasets for a case."""
    pass


@router.post("/{workshop_id}/cases/{case_id}/obd_data")
def add_obd_data(workshop_id: str, case_id: str, obd_data: None):
    """Add a new obd dataset to a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/obd_data/{data_id}")
def get_obd_data(workshop_id: str, case_id: str, data_id: str):
    """Get a specific obd dataset from a case."""
    pass


@router.put("/{workshop_id}/cases/{case_id}/obd_data/{data_id}")
def update_obd_data(workshop_id: str, case_id: str, data_id: str):
    """Update a specific obd dataset of a case."""
    pass


@router.delete("/{workshop_id}/cases/{case_id}/obd_data/{data_id}")
def delete_obd_data(workshop_id: str, case_id: str, data_id):
    """Delete a specific obd dataset from a case."""
    pass


@router.get("/{workshop_id}/cases/{case_id}/symptoms")
def list_symptoms(workshop_id: str, case_id: str):
    pass


@router.post("/{workshop_id}/cases/{case_id}/symptoms")
def add_symptom(workshop_id: str, case_id: str):
    pass


@router.get("/{workshop_id}/cases/{case_id}/symptoms/{component}")
def get_symptom(workshop_id: str, case_id: str, component: Component):
    pass


@router.put("/{workshop_id}/cases/{case_id}/symptoms/{component}")
def update_symptom(workshop_id: str, case_id: str, component: str):
    pass


@router.delete("/{workshop_id}/cases/{case_id}/symptoms/{component}")
def delete_symptom(workshop_id: str, case_id: str, component: str):
    pass
