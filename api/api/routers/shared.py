from typing import List

from fastapi import APIRouter, HTTPException

from ..data_management import Case, Customer, Vehicle, Workshop

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
    case = await Case.get(case_id)
    if case is not None:
        return case
    else:
        exception_detail = f"No case with id `{case_id}`"
        raise HTTPException(status_code=404, detail=exception_detail)


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
