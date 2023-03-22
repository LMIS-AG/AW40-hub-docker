import pytest
from motor import motor_asyncio
from bson import ObjectId


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


@pytest.fixture
def timeseries_meta_data():
    """Valid timeseries meta data"""
    return {
        "component": "Batterie",
        "label": "keine Angabe",
        "sampling_rate": 1,
        "duration": 3,
        "type": "oscillogram"
    }


@pytest.fixture
def timeseries_signal_id():
    """Valid timeseries signal id, e.g. needs to work with PydanticObjectId"""
    return str(ObjectId())


@pytest.fixture
def timeseries_data(timeseries_meta_data, timeseries_signal_id):
    """Data expected to validate successfully with TimeseriesData"""
    timeseries_meta_data["signal_id"] = timeseries_signal_id
    return timeseries_meta_data


@pytest.fixture
def timeseries_signal():
    return [-1.0, 0, 1.0]


@pytest.fixture
def new_timeseries_data(timeseries_meta_data, timeseries_signal):
    """Data expected to validate successfully with NewTimeseriesData"""
    timeseries_meta_data["signal"] = timeseries_signal
    return timeseries_meta_data
