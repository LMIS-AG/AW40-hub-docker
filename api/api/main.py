from beanie import init_beanie
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor import motor_asyncio

from .data_management import (
    Case, Vehicle, Customer, Workshop, TimeseriesMetaData
)
from .data_management.timeseries_data import GridFSSignalStore
from .settings import settings
from .v1 import api_v1
from .storage.storage_factory import StorageFactory

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=["*"],
)
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
def init_storages():
    StorageFactory.initialise_storages(
        minio_host=settings.minio_host,
        minio_password=settings.minio_password,
        minio_username=settings.minio_username
    )
