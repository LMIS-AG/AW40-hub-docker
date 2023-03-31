from datetime import datetime
from enum import Enum
from typing import List, Any, Union

from beanie import Document, Indexed, before_event, Insert, Delete
from pydantic import BaseModel, Field, NonNegativeInt

from .customer import Customer
from .obd_data import OBDData
from .symptom import Symptom
from .timeseries_data import TimeseriesData, NewTimeseriesData
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
    timeseries_data: List[Union[TimeseriesData, None]] = []
    obd_data: List[Union[OBDData, None]] = []
    symptoms: List[Union[Symptom, None]] = []

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

    async def add_timeseries_data(self, new_data: NewTimeseriesData):
        # signal data is stored and converted to ref
        timeseries_data = await new_data.to_timeseries_data()

        # case is updated and returned
        self.timeseries_data.append(timeseries_data)
        await self.save()
        return self

    @staticmethod
    def validate_data_id(data_id: NonNegativeInt):
        if isinstance(data_id, int) and data_id >= 0:
            pass
        else:
            raise ValueError(
                f"Expected non-negative int for data_id but got {data_id}"
            )

    @staticmethod
    def get_data_from_array(
            data_array: list, data_id: NonNegativeInt
    ) -> Any:
        Case.validate_data_id(data_id)
        try:
            return data_array[data_id]
        except IndexError:
            return None

    def get_timeseries_data(self, data_id: NonNegativeInt) -> TimeseriesData:
        return self.get_data_from_array(self.timeseries_data, data_id=data_id)

    def get_obd_data(self, data_id: NonNegativeInt) -> OBDData:
        return self.get_data_from_array(self.obd_data, data_id=data_id)

    def get_symptom(self, data_id: NonNegativeInt) -> Symptom:
        return self.get_data_from_array(self.symptoms, data_id=data_id)

    async def delete_timeseries_data(self, data_id: NonNegativeInt):
        timeseries_data = self.get_timeseries_data(data_id)
        if timeseries_data is not None:
            await timeseries_data.delete_signal()
            self.timeseries_data[data_id] = None
            await self.save()

    async def delete_obd_data(self, data_id: NonNegativeInt):
        obd_data = self.get_obd_data(data_id)
        if obd_data is not None:
            self.obd_data[data_id] = None
            await self.save()

    async def delete_symptom(self, data_id: NonNegativeInt):
        symptom = self.get_symptom(data_id)
        if symptom is not None:
            self.symptoms[data_id] = None
            await self.save()

    @property
    def available_timeseries_data(self):
        return [i for i, d in enumerate(self.timeseries_data) if d is not None]

    @property
    def available_obd_data(self):
        return [i for i, d in enumerate(self.obd_data) if d is not None]

    @property
    def available_symptoms(self):
        return [i for i, d in enumerate(self.symptoms) if d is not None]

    @before_event(Delete)
    async def _delete_all_timeseries_signals(self):
        """
        Makes sure that binary signal data stored outside of case is also
        removed.
        """
        for ts in self.timeseries_data:
            if ts is not None:
                await ts.delete_signal()
