from typing import ClassVar

from beanie import Document


class Customer(Document):

    class Settings:
        name = "customers"

    id: str

    # a unknown id is needed is needed to allow indexing cases by customer
    unknown_id: ClassVar[str] = "unknown"
