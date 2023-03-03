from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from .vehicle import Component


class SymptomLabel(str, Enum):
    unkown = "keine Angabe"
    ok = "nicht defekt"
    defect = "defekt"


class Symptom(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    component: Component
    label: SymptomLabel
