from typing import List

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Depends

from ..data_management import Case, Customer, Vehicle, Workshop
from ..diagnostics_management import DiagnosticTaskManager

tags_metadata = [
    {
        "name": "Shared",
        "description": "Read access to shared ressources"
    }
]


router = APIRouter(tags=["Shared"])


@router.get("/cases", status_code=200, response_model=List[Case])
async def list_cases(
        customer_id: str = None,
        vin: str = None,
        workshop_id: str = None
) -> List[Case]:
    """
    List all cases in Hub. Query params can be used to filter by `customer_id`,
    `vin` and `workshop_id`.
    """
    cases = await Case.find_in_hub(
        customer_id=customer_id, vin=vin, workshop_id=workshop_id
    )
    return cases


@router.get("/cases/{case_id}", status_code=200, response_model=Case)
async def get_case(case_id: str) -> Case:
    no_case_exception = HTTPException(
        status_code=404, detail=f"No case with id `{case_id}`"
    )
    try:
        case_id = ObjectId(case_id)
    except InvalidId:
        # invalid id reports not found to user
        raise no_case_exception

    case = await Case.get(case_id)
    if case is not None:
        return case
    else:
        raise no_case_exception


@router.get("/customers", status_code=200, response_model=List[Customer])
async def list_customers() -> List[Customer]:
    """
    List all customers in Hub.
    """
    customers = await Customer.find_all().to_list()
    return customers


@router.get(
    "/customers/{customer_id}", status_code=200, response_model=Customer
)
async def get_customer(customer_id: str) -> Customer:
    customer = await Customer.get(customer_id)
    if customer is not None:
        return customer
    else:
        exception_detail = f"No customer with id `{customer_id}`"
        raise HTTPException(status_code=404, detail=exception_detail)


@router.get("/vehicles", status_code=200, response_model=List[Vehicle])
async def list_vehicles() -> List[Vehicle]:
    """
    List all vehicles in Hub.
    """
    vehicles = await Vehicle.find_all().to_list()
    return vehicles


@router.get(
    "/known-components", status_code=200, response_model=List[str]
)
async def list_vehicle_components(
        diagnostic_task_manager: DiagnosticTaskManager =
        Depends(DiagnosticTaskManager)
) -> List[str]:
    """List all vehicle component names known to the Hub's diagnostic
    backend.
    """
    components = diagnostic_task_manager.get_vehicle_components()
    return components


@router.get("/vehicles/{vin}", status_code=200, response_model=Vehicle)
async def get_vehicle(vin: str) -> Vehicle:
    vehicle = await Vehicle.find_one({"vin": vin})
    if vehicle is not None:
        return vehicle
    else:
        exception_detail = f"No vehicle with vin `{vin}`"
        raise HTTPException(status_code=404, detail=exception_detail)


@router.get("/workshops", status_code=200, response_model=List[Workshop])
async def list_workshops() -> List[Workshop]:
    """
    Get all workshops in Hub.
    """
    workshops = await Workshop.find_all().to_list()
    return workshops


@router.get(
    "/workshops/{workshop_id}", status_code=200, response_model=Workshop
)
async def get_workshop(workshop_id: str) -> Workshop:
    workshop = await Workshop.get(workshop_id)
    if workshop is not None:
        return workshop
    else:
        exception_detail = f"No workshop with id `{workshop_id}`"
        raise HTTPException(status_code=404, detail=exception_detail)
