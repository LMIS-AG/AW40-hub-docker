from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel


class Component(str, Enum):
    """All the components that a vehicle can have."""
    batterie = "Batterie"
    luftmassenmesser = "Luftmassenmesser"
    lambda_sonde_vor_kat = "Lambda Sonde (vor Kat)"
    lambda_sonde_nach_kat = "Lambda Sonde (nach Kat)"


class Vehicle(Document):

    class Config:
        # 'vin' is used instead of 'id'
        fields = {"id": {"exclude": True}}

    class Settings:
        name = "vehicles"

    vin: Indexed(str, unique=True)
    tsn: str = None
    year_build: int = None


class VehicleUpdate(BaseModel):
    tsn: str = None
    year_build: int = None
