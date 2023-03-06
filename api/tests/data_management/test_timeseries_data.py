import pytest
from api.data_management.timeseries_data import GridFSSignalStore
from motor import motor_asyncio


@pytest.fixture
def signal_bucket(motor_db):
    test_bucket_name = "signals-pytest"  # dedicated test bucket
    test_bucket = motor_asyncio.AsyncIOMotorGridFSBucket(
        motor_db, bucket_name=test_bucket_name
    )
    yield test_bucket

    # teardown by dropping the test bucket gridfs collections
    motor_db.drop_collection(f"{test_bucket_name}.files")
    motor_db.drop_collection(f"{test_bucket_name}.chunks")


class TestGridFSSignalStore:

    @pytest.mark.asyncio
    async def test_create_and_get(self, signal_bucket):
        signal_store = GridFSSignalStore(signal_bucket)
        signal = [-1., 0., 1]
        signal_id = await signal_store.create(signal)
        retrieved_signal = await signal_store.get(signal_id)
        assert signal == retrieved_signal
