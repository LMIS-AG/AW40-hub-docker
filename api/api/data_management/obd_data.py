from datetime import datetime
from typing import List, Any

from pydantic import BaseModel, Field, constr


class OBDData(BaseModel):

    class Config:
        schema_extra = {
            "example": {
                "dtcs": ["P0001", "U0001"]
            }
        }

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    dtcs: List[constr(min_length=5, max_length=5)]
    obd_specs: dict = None
