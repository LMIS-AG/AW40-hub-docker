from beanie import init_beanie
from fastapi import FastAPI
from motor import motor_asyncio

from .data_management import (
    Case, Vehicle, Customer, Workshop, TimeseriesMetaData
)
from .data_management.timeseries_data import GridFSSignalStore
from .diagnostics_management import GetCelery
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

    # initialized gridfs signal storage
    bucket = motor_asyncio.AsyncIOMotorGridFSBucket(
        client[settings.mongo_db], bucket_name="signals"
    )
    TimeseriesMetaData.signal_store = GridFSSignalStore(bucket=bucket)


@app.on_event("startup")
async def init_celery():
    GetCelery.broker = settings.redis_uri
    GetCelery.backend = settings.redis_uri
