from beanie import init_beanie
from fastapi import FastAPI
from motor import motor_asyncio

from .data_management import Case, Vehicle, Customer, Workshop
from .settings import settings
from .v1 import api_v1

app = FastAPI()

app.mount("/v1", api_v1)


@app.on_event("startup")
async def init_mongo():

    # initialize beanie
    client = motor_asyncio.AsyncIOMotorClient(settings.mongo_uri)
    await init_beanie(
        client[settings.mongo_db],
        document_models=[Case, Vehicle, Customer, Workshop]
    )
