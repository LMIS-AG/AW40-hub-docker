from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, constr


class OBDMetaData(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    obd_specs: dict = None


class OBDData(OBDMetaData):

    class Config:
        schema_extra = {
            "example": {
                "dtcs": ["P0001", "U0001"]
            }
        }

    dtcs: List[constr(min_length=5, max_length=5)]
