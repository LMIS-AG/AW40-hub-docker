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
    Use database 'aw40-hub-test'. Database 'aw40-hub' ist defined in dev.env
    and hence mongo/init-users.sh should have created readWrite role for
    api user.
    """
    yield motor_client["aw40-hub-test"]
