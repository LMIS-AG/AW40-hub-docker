from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, NonNegativeInt

from .vehicle import Component


class SymptomLabel(str, Enum):
    unkown = "keine Angabe"
    ok = "nicht defekt"
    defect = "defekt"


class NewSymptom(BaseModel):
    """Schema for a new symptom."""
    class Config:
        schema_extra = {
            "example": {
                "component": "Batterie",
                "label": "defekt"
            }
        }

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    component: Component
    label: SymptomLabel


class Symptom(NewSymptom):
    data_id: NonNegativeInt = None


class SymptomUpdate(BaseModel):
    """Same fields as NewSymptom but all fields are optional."""

    class Config:
        schema_extra = {
            "example": {
                "label": "defekt"
            }
        }

    timestamp: datetime = None
    component: Component = None
    label: SymptomLabel = None
