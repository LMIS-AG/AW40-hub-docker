import pytest
from motor import motor_asyncio


@pytest.fixture
def motor_client():
    """
    Assume a local mongodb instance is available with credentials as in dev.env
    """
    mongo_uri = "mongodb://mongo-api-user:mongo-api-pw@127.0.0.1:27017/" \
                "?authSource=admin"
    return motor_asyncio.AsyncIOMotorClient(mongo_uri)


@pytest.fixture
def motor_db(motor_client):
    """
    Use database defined in dev.env (otherwise credentials
    mongo-api-user:mongo-api-pw used in motor_client will not work. Hence,
    make sure to use dedicated test collections.
    """
    return motor_client["aw40-hub"]
