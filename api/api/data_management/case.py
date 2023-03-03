from datetime import datetime
from enum import Enum
from typing import List

from beanie import Document, Indexed, before_event, Insert
from pydantic import BaseModel, Field

from .customer import Customer
from .obd_data import OBDData
from .symptom import Symptom
from .vehicle import Vehicle


class Occasion(str, Enum):
    unkown = "keine Angabe"
    service_routine = "Service / Routine"
    problem_defect = "Problem / Defekt"


class Status(str, Enum):
    open = "offen"
    closed = "abgeschlossen"


class NewCase(BaseModel):
    """Schema for new cases added via the api."""

    class Config:
        schema_extra = {
            "example": {
                "vehicle_vin": "VIN42",
                "customer_id": "firstname.lastname",
                "occasion": Occasion.service_routine,
                "milage": 42
            }
        }

    vehicle_vin: str
    customer_id: Indexed(str, unique=False) = Customer.unknown_id
    occasion: Occasion = Occasion.unkown
    milage: int = None


class Case(Document):
    """Complete case schema and major db interfacing class."""

    class Config:
        validate_assignment = True
        fields = {"schema_version": {"exclude": True}}

    class Settings:
        name = "cases"

    # case descriptions
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    occasion: Occasion = Occasion.unkown
    milage: int = None
    status: Status = Status.open

    # foreign keys
    customer_id: Indexed(str, unique=False) = Customer.unknown_id
    vehicle_vin: Indexed(str, unique=False)
    workshop_id: Indexed(str, unique=False)

    # diagnostic data
    timeseries_data: str = None
    obd_data: List[OBDData] = []
    symptoms: List[Symptom] = []

    schema_version: int = 0

    @before_event(Insert)
    async def insert_vehicle(self):
        """
        Create the vehicle if non-existent, e.g. if it is the first case for
        this vehicle.
        """
        vehicle = await Vehicle.find_one({"vin": self.vehicle_vin})
        if vehicle is None:
            vehicle = Vehicle(vin=self.vehicle_vin)
            await vehicle.insert()

    @before_event(Insert)
    async def insert_customer(self):
        """
        Create the customer if non-existent, e.g. if it is the first case for
        this customer.
        """
        customer = await Customer.get(self.customer_id)
        if customer is None:
            customer = Customer(id=self.customer_id)
            await customer.insert()

    @classmethod
    async def find_in_hub(
            cls,
            customer_id: str = None,
            vin: str = None,
            workshop_id: str = None
    ):
        """
        Get list of all cases filtered by customer_id, vehicle_vin and
        workshop_id.
        """
        filter = {}
        if customer_id is not None:
            filter["customer_id"] = customer_id
        if vin is not None:
            filter["vehicle_vin"] = vin
        if workshop_id is not None:
            filter["workshop_id"] = workshop_id

        cases = await cls.find(filter).to_list()
        return cases

