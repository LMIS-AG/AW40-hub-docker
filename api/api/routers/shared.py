from typing import List

from fastapi import APIRouter

from ..data_management import Case, Customer, Vehicle, Workshop

tags_metadata = [
    {
        "name": "Shared",
        "description": "Read access to shared ressources"
    }
]


router = APIRouter(tags=["Shared"])


@router.get("/cases")
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


@router.get("/cases/{case_id}")
async def get_case(case_id: str) -> Case:
    case = await Case.get(case_id)
    return case


@router.get("/customers")
async def list_customers(
        vin: str = None, workshop_id: str = None
) -> List[Customer]:
    """
    List all customers in Hub. Query params can be used to filter by `vin` and
    `workshop_id`.
    """
    pass


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str) -> Customer:
    pass


@router.get("/vehicles")
async def list_vehicles(
        customer_id: str = None, workshop_id: str = None
) -> List[Vehicle]:
    """
    List all vehicles in Hub. Query params can be used to filter by
    `customer_id` and `workshop_id`.
    """
    pass


@router.get("/vehicles/{vin}")
async def get_vehicle(vin: str) -> Vehicle:
    pass


@router.get("/workshops")
async def list_workshops(
        customer_id: str = None, vin: str = None
) -> List[Workshop]:
    """
    Get all workshops in Hub. Query params can be used to filter by
    `customer_id` and `vin`.
    """
    pass


@router.get("/workshops/{workshop_id}")
async def get_workshop(workshop_id: str) -> Workshop:
    pass
