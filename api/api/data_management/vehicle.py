from enum import Enum

from beanie import Document, Indexed


class Component(str, Enum):
    """All the components that a vehicle can have."""
    battery = "Batterie"
    motor = "Motor"


class Vehicle(Document):

    class Config:
        # 'vin' is used instead of 'id'
        fields = {"id": {"exclude": True}}

    class Settings:
        name = "vehicles"

    vin: Indexed(str, unique=True)
    tsn: str = None
    year_build: int = None
