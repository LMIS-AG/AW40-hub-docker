from datetime import datetime
from enum import Enum
from typing import List, Optional

from beanie import Document, Indexed, PydanticObjectId
from motor import motor_asyncio
from pydantic import BaseModel, Field


class Action(BaseModel):
    """Describes an action, that can be required of an user"""

    id: str = None
    instruction: str

    action_type: str = None
    data_type: str = None
    component: str = None


class DiagnosisStatus(str, Enum):
    scheduled = "scheduled"
    action_required = "action_required"
    processing = "processing"
    finished = "finished"
    failed = "failed"


class DiagnosisLogEntry(BaseModel):
    message: str
    attachment: Optional[PydanticObjectId] = None


class AttachmentBucket:
    bucket: motor_asyncio.AsyncIOMotorGridFSBucket = None

    @classmethod
    def create(cls):
        """
        Factory to use in endpoints handlers to create gridfs bucket
        to store attachments
        """
        if cls.bucket is None:
            raise AttributeError("No bucket configured to store attachments")
        return cls.bucket


class Diagnosis(Document):
    """Internal Diagnosis Representation"""

    class Settings:
        name = "diagnosis"

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: DiagnosisStatus = None
    state_machine_log: List[DiagnosisLogEntry] = []
    case_id: Indexed(PydanticObjectId, unique=True)
    todos: List[Action] = []
