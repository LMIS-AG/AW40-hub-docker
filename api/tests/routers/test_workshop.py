from collections import namedtuple
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, UTC
from tempfile import TemporaryFile
from unittest import mock

import bson
import pytest
from api.data_management import (
    TimeseriesData,
    NewTimeseriesData,
    OBDData,
    NewOBDData,
    Symptom,
    Case,
    Vehicle,
    Customer,
    Workshop,
    Diagnosis,
    DiagnosisStatus
)
from api.routers.workshop import (
    router, case_from_workshop, DiagnosticTaskManager
)
from api.security.keycloak import Keycloak
from beanie import init_beanie
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from httpx import (
    AsyncClient,
    ASGITransport
)
from jose import jws


@pytest.fixture
def workshop_id():
    return "test-workshop"


@pytest.fixture
def case_id():
    """Valid case_id, e.g. needs to work with PydanticObjectId"""
    return "5eb7cf5a86d9755df3a6c593"


@pytest.fixture
def case_data(case_id, workshop_id):
    """Valid (minimal) case data."""
    return {
        "_id": case_id,
        "vehicle_vin": "test-vin",
        "workshop_id": workshop_id,
    }


@pytest.fixture
def obd_data():
    """Valid obd data."""
    return {"dtcs": ["P0001", "U0001"]}


@pytest.fixture
def symptom():
    """Valid symptom data."""
    return {"component": "battery", "label": "defect"}


@pytest.fixture
def app(motor_db):
    """
    Request this fixture to test routes via TestClient(app) as described
    in https://fastapi.tiangolo.com/tutorial/testing/.
    If a test requires beanie initialization, (e.g. because a non-mock
    instance of a beanie doc is created at some point) this fixture needs to
    be used in a with statement (e.g. with TestClient(app) as client: ...)
    Using a with statement ensures execution of the test applications startup
    and shutdown handlers used for beanie/mongo setup and teardown
    (see https://fastapi.tiangolo.com/advanced/testing-events/).
    """

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        await init_mongo()
        yield
        await teardown_mongo()

    app = FastAPI(lifespan=lifespan)
    app.include_router(router)

    models = [
        Case, Vehicle, Customer, Workshop, Diagnosis
    ]

    async def init_mongo():
        await init_beanie(
            motor_db,
            document_models=models
        )
        for model in models:
            # make sure all collections are empty at the beginning of each
            # test
            await model.delete_all()

    async def teardown_mongo():
        for model in models:
            await model.get_motor_collection().drop()
            await model.get_motor_collection().drop_indexes()

    yield app


@pytest.fixture
def jwt_payload(workshop_id):
    return {
        "iat": datetime.now(UTC).timestamp(),
        "exp": (datetime.now(UTC) + timedelta(60)).timestamp(),
        "preferred_username": workshop_id,
        "realm_access": {"roles": ["workshop"]}
    }


@pytest.fixture
def signed_jwt(jwt_payload, rsa_private_key_pem: bytes):
    """Create a JWT signed with private RSA key."""
    return jws.sign(jwt_payload, rsa_private_key_pem, algorithm="RS256")


@pytest.fixture
def unauthenticated_client(app):
    """Unauthenticated client, e.g. no bearer token in header."""
    yield TestClient(app)


@pytest.fixture
def authenticated_client(
        unauthenticated_client, rsa_public_key_pem, signed_jwt
):
    """Turn unauthenticated client into authenticated client."""

    # Client gets auth header with valid bearer token
    client = unauthenticated_client
    client.headers.update({"Authorization": f"Bearer {signed_jwt}"})

    # Make app use public key from fixture for token validation
    app = client.app
    app.dependency_overrides[
        Keycloak.get_public_key_for_workshop_realm
    ] = lambda: rsa_public_key_pem.decode()

    return client


@mock.patch("api.routers.workshop.Case.find_in_hub", autospec=True)
def test_list_cases(find_in_hub, authenticated_client, workshop_id):
    async def mock_find_in_hub(
            customer_id,
            workshop_id,
            vin,
            obd_data_dtc,
            timeseries_data_component
    ):
        return []

    # patch Case.find_in_hub to use mock_find_in_hub
    find_in_hub.side_effect = mock_find_in_hub

    # request without params
    response = authenticated_client.get(f"/{workshop_id}/cases")

    # confirm expected response and usage of db interface
    assert response.status_code == 200
    assert response.json() == []
    find_in_hub.assert_called_once_with(
        customer_id=None,
        vin=None,
        workshop_id=workshop_id,
        obd_data_dtc=None,
        timeseries_data_component=None
    )


@mock.patch("api.routers.workshop.Case.find_in_hub", autospec=True)
def test_list_cases_with_filters(
        find_in_hub, authenticated_client, workshop_id
):
    async def mock_find_in_hub(
            customer_id,
            workshop_id,
            vin,
            obd_data_dtc,
            timeseries_data_component
    ):
        return []

    # patch Case.find_in_hub to use mock_find_in_hub
    find_in_hub.side_effect = mock_find_in_hub

    # request with filter params
    customer_id = "test customer"
    vin = "test vin"
    obd_data_dtc = "P0001"
    timeseries_data_component = "Test-Comp"
    response = authenticated_client.get(
        f"/{workshop_id}/cases",
        params={
            "customer_id": customer_id,
            "vin": vin,
            "obd_data_dtc": obd_data_dtc,
            "timeseries_data_component": timeseries_data_component
        }
    )

    # confirm expected response and usage of db interface
    assert response.status_code == 200
    assert response.json() == []
    find_in_hub.assert_called_once_with(
        customer_id=customer_id,
        vin=vin,
        workshop_id=workshop_id,
        obd_data_dtc=obd_data_dtc,
        timeseries_data_component=timeseries_data_component
    )


def test_add_case(authenticated_client, workshop_id):
    new_case = {
        "vehicle_vin": "test-vin",
        "occasion": "unknown",
        "milage": 42
    }
    with authenticated_client as client:
        response = client.post(f"/{workshop_id}/cases", json=new_case)

    assert response.status_code == 201
    assert response.json()["_id"] is not None


@pytest.mark.parametrize(
    "customer_id",
    [
        "not-an-object-id",  # invalid format
        str(bson.ObjectId())  # invalid as no customer with this id exists
    ]
)
def test_add_case_with_invalid_customer_id(
        authenticated_client, workshop_id, customer_id
):
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases",
            json={"vehicle_vin": "v", "customer_id": customer_id}
        )
    assert response.status_code == 422


@mock.patch("api.routers.workshop.Case.get", autospec=True)
@pytest.mark.asyncio
async def test_case_from_workshop(get, case_id, workshop_id):
    async def mock_get(*args):
        """
        Always returns a case with case_id and workshop_id predefined in test
        scope above.
        """
        Case = namedtuple("Case", ["case_id", "workshop_id"])
        case = Case(case_id=case_id, workshop_id=workshop_id)
        return case

    # patch Case.get to use mock_get instead
    get.side_effect = mock_get

    # case_from_workshop should return the case defined in mock_get as is
    case = await case_from_workshop(workshop_id=workshop_id, case_id=case_id)
    assert case.case_id == case_id


@mock.patch("api.routers.workshop.Case.get", autospec=True)
@pytest.mark.asyncio
async def test_case_from_workshop_is_none(get, case_id):
    async def mock_get(*args):
        """Always returns None, e.g. no case found."""
        return None

    # patch Case.get to use mock_get instead
    get.side_effect = mock_get

    # since there is no case, a 404 should be raised
    with pytest.raises(HTTPException) as excinfo:
        await case_from_workshop(workshop_id="anything", case_id=case_id)
    assert excinfo.value.status_code == 404


@mock.patch("api.routers.workshop.Case.get", autospec=True)
@pytest.mark.asyncio
async def test_case_from_workshop_wrong_workshop(get, case_id, workshop_id):
    async def mock_get(*args):
        """
        Always returns a case with case_id as predifined in test scope above
        but different workshop id.
        """
        Case = namedtuple("Case", ["case_id", "workshop_id"])
        another_workshop_id = "another test workshop"
        case = Case(case_id=case_id, workshop_id=another_workshop_id)
        return case

    # patch Case.get to use mock_get instead
    get.side_effect = mock_get

    # since case belongs to another workshop, a 404 should be raised
    with pytest.raises(HTTPException) as excinfo:
        await case_from_workshop(workshop_id=workshop_id, case_id=case_id)
    assert excinfo.value.status_code == 404


@pytest.mark.asyncio
async def test_case_from_workshop_invalid_case_id_format():
    case_id = "this is not a valid ObjectId"
    workshop_id = "test workshop"

    # case_id will result in internal exception, as it is not a valid bson
    # ObjectId. This should just be reported as not found to the api user
    with pytest.raises(HTTPException) as excinfo:
        await case_from_workshop(workshop_id=workshop_id, case_id=case_id)
    assert excinfo.value.status_code == 404


def test_get_case(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}"
        )

    # confirm expected status code and response schema
    assert response.status_code == 200
    assert Case(**response.json())


@mock.patch("api.routers.workshop.Case.set", autospec=True)
def test_update_case(case_set, case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    case_data["status"] = "open"
    new_status = "closed"

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.set with AsyncMock to confirm use with await
    case_set.side_effect = mock.AsyncMock()

    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}",
            json={"status": new_status}
        )

    # confirm expected status code and response schema
    assert response.status_code == 200
    assert Case(**response.json())

    # confirm await of Case.set
    case_set.side_effect.assert_awaited_once()


def test_delete_case(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}"
        )
    assert response.status_code == 200


def test_list_timeseries_data(
        case_data, timeseries_data, authenticated_client
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add timeseries_data multiple times to case_data
    repeats = 2
    case_data["timeseries_data"] = repeats * [timeseries_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data"
        )

    # confirm expected status code and response shape
    assert response.status_code == 200
    assert len(response.json()) == repeats


def mock_add_timeseries_data(signal_id):
    """
    Create a test mock for Case.add_timeseries_data that does not require
    setup of storage backend and uses a fixed signal_id.
    """

    async def add_timeseries_data(self, new_data: NewTimeseriesData):
        # exchange signal and signal_id without accessing signal store
        meta_data = new_data.model_dump(exclude={"signal"})
        meta_data["signal_id"] = signal_id
        timeseries_data = TimeseriesData(**meta_data)

        # append to case without saving
        self.timeseries_data.append(timeseries_data)
        return self

    return add_timeseries_data


@mock.patch("api.routers.workshop.Case.add_timeseries_data", autospec=True)
def test_add_timeseries_data(
        add_timeseries_data,
        case_data,
        new_timeseries_data,
        authenticated_client,
        timeseries_signal_id
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.add_timeseries_data to call mock instead
    add_timeseries_data.side_effect = mock_add_timeseries_data(
        signal_id=timeseries_signal_id
    )

    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data",
            json=new_timeseries_data
        )

    # confirm expected status code and response shape
    assert response.status_code == 201
    assert len(response.json()["timeseries_data"]) == 1


@pytest.mark.parametrize(
    "file,file_format",
    [
        ("picoscope_1ch_eng_csv_file", "Picoscope CSV"),
        ("picoscope_1ch_ger_csv_file", "Picoscope CSV"),
        ("picoscope_4ch_eng_csv_file", "Picoscope CSV"),
        ("picoscope_4ch_ger_csv_file", "Picoscope CSV"),
        ("picoscope_8ch_ger_comma_decimal_csv_file", "Picoscope CSV"),
        ("picoscope_1ch_mat_file", "Picoscope MAT"),
        ("picoscope_4ch_mat_file", "Picoscope MAT")
    ]
)
@mock.patch("api.routers.workshop.Case.add_timeseries_data", autospec=True)
def test_upload_picoscope_data_single_channel(
        add_timeseries_data,
        file,
        file_format,
        case_data,
        authenticated_client,
        timeseries_signal_id,
        request
):
    # use request fixture to convert file parameter from str to actual
    # value of picoscope file fixture
    file = request.getfixturevalue(file)

    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.add_timeseries_data to call mock instead
    add_timeseries_data.side_effect = mock_add_timeseries_data(
        signal_id=timeseries_signal_id
    )

    # upload file and only specify component for one channel
    channel = "A"
    component = "maf_sensor"
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/upload/picoscope",
            files={"upload": ("filename", file)},
            data={
                f"component_{channel}": component, "file_format": file_format
            }
        )

    # confirm expected status code and response data
    assert response.status_code == 201
    timeseries_data = response.json()["timeseries_data"]
    assert len(timeseries_data) == 1
    assert timeseries_data[0]["device_specs"]["channel"] == channel
    assert timeseries_data[0]["component"] == component


@pytest.mark.parametrize(
    "file,file_format",
    [
        ("picoscope_4ch_eng_csv_file", "Picoscope CSV"),
        ("picoscope_4ch_ger_csv_file", "Picoscope CSV"),
        ("picoscope_8ch_ger_comma_decimal_csv_file", "Picoscope CSV"),
        ("picoscope_4ch_mat_file", "Picoscope MAT")
    ]
)
@mock.patch("api.routers.workshop.Case.add_timeseries_data", autospec=True)
def test_upload_picoscope_data_multi_channel(
        add_timeseries_data,
        file,
        file_format,
        case_data,
        authenticated_client,
        timeseries_signal_id,
        request
):
    # use request fixture to convert file parameter from str to actual
    # value of picoscope file fixture
    file = request.getfixturevalue(file)

    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.add_timeseries_data to call mock instead
    add_timeseries_data.side_effect = mock_add_timeseries_data(
        signal_id=timeseries_signal_id
    )

    # upload file and specify components for two channels
    channel_0 = "B"
    component_0 = "maf_sensor"
    channel_1 = "C"
    component_1 = "battery"
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/upload/picoscope",
            files={"upload": ("filename", file)},
            data={
                f"component_{channel_0}": component_0,
                f"component_{channel_1}": component_1,
                "file_format": file_format
            }
        )

    # confirm expected status code and response data
    assert response.status_code == 201
    timeseries_data = response.json()["timeseries_data"]
    assert len(timeseries_data) == 2
    assert timeseries_data[0]["device_specs"]["channel"] == channel_0
    assert timeseries_data[0]["component"] == component_0
    assert timeseries_data[1]["device_specs"]["channel"] == channel_1
    assert timeseries_data[1]["component"] == component_1


@pytest.mark.parametrize(
    "file,file_format",
    [
        ("picoscope_1ch_eng_csv_file", "Picoscope CSV"),
        ("picoscope_1ch_ger_csv_file", "Picoscope CSV"),
        ("picoscope_1ch_mat_file", "Picoscope MAT")
    ]
)
def test_upload_picoscope_data_wrong_channel_specs(
        file,
        file_format,
        case_data,
        authenticated_client,
        request
):
    # use request fixture to convert file parameter from str to actual
    # value of picoscope file fixture
    file = request.getfixturevalue(file)

    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # upload file and only specify component for channel B, even though files
    # only have channel A
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/upload/picoscope",
            files={"upload": ("filename", file)},
            data={
                "component_B": "battery",
                "file_format": file_format
            }
        )

    # confirm expected http exception
    assert response.status_code == 400


@pytest.mark.parametrize("file_format", ["Picoscope MAT", "Picoscope CSV"])
def test_upload_picoscope_data_wrong_file(
        file_format,
        case_data,
        authenticated_client,
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # upload wrong file
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/upload/picoscope",
            files={"upload": ("filename", TemporaryFile())},
            data={"componant_A": "battery", "file_format": file_format}
        )

    # confirm expected http exception
    assert response.status_code == 400


@mock.patch("api.routers.workshop.Case.add_obd_data", autospec=True)
def test_upload_vcds_data(
        add_obd_data, case_data, obd_data, vcds_txt_file, authenticated_client
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.add_obd_data to use mock
    add_obd_data.side_effect = mock_add_obd_data()

    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/obd_data/upload/vcds",
            files={"upload": ("filename", vcds_txt_file)}
        )

    # confirm expected status code and response shape
    assert response.status_code == 201
    assert len(response.json()["obd_data"]) == 1


@pytest.mark.parametrize(
    "file,device_id",
    [
        ("omniview_csv_file", "E46920935F320D2D"),
        ("omniview_sin_csv_file", "E46228B163272D25")
    ]
)
@mock.patch("api.routers.workshop.Case.add_timeseries_data", autospec=True)
def test_upload_omniview_data(
        add_timeseries_data,
        file, device_id, request,
        case_data,
        authenticated_client,
        timeseries_signal_id
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.add_timeseries_data to call mock instead
    add_timeseries_data.side_effect = mock_add_timeseries_data(
        signal_id=timeseries_signal_id
    )

    # upload file and only specify component for one channel
    component = "maf_sensor"
    file = request.getfixturevalue(file)
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/upload/omniview",
            files={"upload": ("filename", file)},
            data={
                "component": component, "sampling_rate": 1, "duration": 654119
            }
        )

    # confirm expected status code and response data
    assert response.status_code == 201
    timeseries_data = response.json()["timeseries_data"]
    assert len(timeseries_data) == 1
    assert timeseries_data[0]["device_specs"]["type"] == "omniscope"
    assert timeseries_data[0]["device_specs"]["device_id"] == device_id
    assert timeseries_data[0]["component"] == component


def test_get_timeseries_data_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request timeseries_data with data_id 1 eventhough case does not have
    # any timeseries data
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1"
        )

    # confirm expected status code
    assert response.status_code == 404


def test_get_timeseries_data(case_data, timeseries_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single timeseries data set to the case
    data_id = 42
    timeseries_data["data_id"] = data_id
    case_data["timeseries_data"] = [timeseries_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request timeseries_data with specified data_id, which should exist
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}"
        )

    # confirm expected status code and response schema
    assert response.status_code == 200
    assert TimeseriesData(**response.json())


def test_get_timeseries_data_signal_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request signal from timeseries_data with data_id 1 eventhough case does
    # not have any timeseries data
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1/signal"
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.TimeseriesData.get_signal", autospec=True)
def test_get_timeseries_data_signal(
        get_signal, case_data, timeseries_data, authenticated_client
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single timeseries data set to the case
    data_id = 30
    timeseries_data["data_id"] = data_id
    case_data["timeseries_data"] = [timeseries_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    test_signal = [0., 1., 2.]

    async def mock_get_signal(self):
        return test_signal

    # patch Case.get_signal to use mock_get_signal
    get_signal.side_effect = mock_get_signal

    # request signal from timeseries_data with data_id, which should exist
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}/signal"
        )

    # confirm expected status code and response data
    assert response.status_code == 200
    assert response.json() == test_signal


def create_mock_save():
    """
    Create the closure mock_save that can be used to patch Case.save.
    The second return value saved_cases can be used to confirm correct
    usage of Case.save, e.g. after updating instance attributes and correct
    response data, e.g. representations of saved state.
    """
    saved_cases = []

    async def mock_save(self):
        saved_cases.append(self)
        return self

    return mock_save, saved_cases


def test_update_timeseries_data_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request update of timeseries_data with data_id 1 eventhough case does not
    # have any timeseries data
    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1",
            json={"label": "norm"}
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_update_timeseries_data(
        save, case_data, timeseries_data, authenticated_client
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # define current label and updated label
    old_label = "unknown"
    new_label = "norm"
    timeseries_data["label"] = old_label

    # add a single timeseries_data with old label to the case
    data_id = 0
    timeseries_data["data_id"] = data_id
    case_data["timeseries_data"] = [timeseries_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request update of timeseries_data with data_id, which should exist
    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}",
            json={"label": new_label}
        )

    # confirm expected status code and expected new label
    assert response.status_code == 200
    assert response.json()["label"] == new_label
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case.timeseries_datas after saving
    assert TimeseriesData(**response.json()) == \
           saved_cases[0].timeseries_data[0]


def test_delete_timeseries_data_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request deletion of timeseries_data with data_id 1 eventhough case does
    # not have any timeseriers data
    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1"
        )

    # confirm expected status code (trying to delete a non-existent ressource
    # returns a 200, as desired status is already in place)
    assert response.status_code == 200


@mock.patch("api.routers.workshop.Case.delete_timeseries_data", autospec=True)
def test_delete_timeseries_data(
        delete_timeseries_data,
        case_data,
        timeseries_data,
        authenticated_client
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single timeseries_data to the case
    data_id = 7
    timeseries_data["data_id"] = data_id
    case_data["timeseries_data"] = [timeseries_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.delete_timeseries_data
    delete_timeseries_data.side_effect = mock.AsyncMock()

    # request deletion of timeseries_data with data_id, which should exist
    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/{data_id}"
        )

    # confirm expected status code and usage of Case.delete_timeseries_data
    assert response.status_code == 200
    delete_timeseries_data.side_effect.assert_awaited_once()


def test_list_obd_data(case_data, obd_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add obd_data multiple times to case_data
    repeats = 2
    case_data["obd_data"] = repeats * [obd_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/obd_data"
        )

    # confirm expected status code and response shape
    assert response.status_code == 200
    assert len(response.json()) == repeats


def mock_add_obd_data():
    """
    Create a test mock for Case.add_obd_data that does not require
    setup of storage backend.
    """

    async def add_obd_data(self, new_obd_data: NewOBDData):
        obd_data = OBDData(
            data_id=self.obd_data_added,
            **new_obd_data.model_dump()
        )
        self.obd_data.append(obd_data)
        self.obd_data_added += 1
        return self

    return add_obd_data


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_add_obd_data(save, case_data, obd_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/obd_data",
            json=obd_data
        )

    # confirm expected status code and response shape
    assert response.status_code == 201
    assert len(response.json()["obd_data"]) == 1
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case after saving
    assert Case(**response.json()) == saved_cases[0]


def test_upload_vcds_data_wrong_file(
        case_data,
        authenticated_client,
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # upload wrong file
    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/obd_data/upload/vcds",
            files={"upload": ("filename", TemporaryFile())}
        )

    # confirm expected http exception
    assert response.status_code == 400


def test_get_obd_data_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request obd_data with data_id 1 eventhough case does not have
    # any obd data
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/obd_data/1"
        )

    # confirm expected status code
    assert response.status_code == 404


def test_get_obd_data(case_data, obd_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single obd data set to the case
    data_id = 5
    obd_data["data_id"] = data_id
    case_data["obd_data"] = [obd_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request obd_data with data_id, which should exist
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/obd_data/{data_id}"
        )

    # confirm expected status code and response shema
    assert response.status_code == 200
    assert OBDData(**response.json())


def test_update_obd_data_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request update of obd_data with data_id 1 eventhough case does not have
    # any obd data
    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/obd_data/1",
            json={"obd_specs": {"some field": "some value"}}
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_update_obd_data(save, case_data, obd_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    old_obd_specs = {"device": "vcds 123"}
    new_obd_specs = {"device": "VCDS"}
    obd_data["obd_specs"] = old_obd_specs

    # add a single obd data set to the case
    data_id = 11
    obd_data["data_id"] = data_id
    case_data["obd_data"] = [obd_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request update of obd_data with data_id, which should exist
    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/obd_data/{data_id}",
            json={"obd_specs": new_obd_specs}
        )

    # confirm expected status code and update of obd specs
    # obd_data
    assert response.status_code == 200
    assert response.json()["obd_specs"] == new_obd_specs
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case.obd_data after saving
    assert OBDData(**response.json()) == saved_cases[0].obd_data[0]


def test_delete_obd_data_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request deletion of obd_data with data_id 1 eventhough case does not have
    # any obd data
    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/obd_data/1"
        )

    # confirm expected status code (trying to delete a non-existent ressource
    # returns a 200, as desired status is already in place)
    assert response.status_code == 200


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_delete_obd_data(save, case_data, obd_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single obd data set to the case
    data_id = 2
    obd_data["data_id"] = data_id
    case_data["obd_data"] = [obd_data]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request deletion of obd_data with data_id, which should exist
    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/obd_data/{data_id}"
        )

    # confirm expected status code and non-existence of previously added
    # obd_data
    assert response.status_code == 200
    assert response.json()["obd_data"] == []
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case after saving
    assert Case(**response.json()) == saved_cases[0]


def test_list_symptoms(case_data, symptom, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add symptom multiple times to case_data
    repeats = 2
    case_data["symptoms"] = repeats * [symptom]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/symptoms"
        )

    # confirm expected status code and response shape
    assert response.status_code == 200
    assert len(response.json()) == repeats


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_add_symptom(save, case_data, symptom, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    with authenticated_client as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/symptoms",
            json=symptom
        )

    # confirm expected status code and response shape
    assert response.status_code == 201
    assert len(response.json()["symptoms"]) == 1
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case after saving
    assert Case(**response.json()) == saved_cases[0]


def test_get_symptom_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request symptom with data_id 1 eventhough case does not have
    # any symptoms
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/symptoms/1"
        )

    # confirm expected status code
    assert response.status_code == 404


def test_get_symptom(case_data, symptom, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single symptom to the case
    data_id = 1
    symptom["data_id"] = data_id
    case_data["symptoms"] = [symptom]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request symptom with data_id, which should exist
    with authenticated_client as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/symptoms/{data_id}"
        )

    # confirm expected status code and response shema
    assert response.status_code == 200
    assert Symptom(**response.json())


def test_update_symptom_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request update of symptom with data_id 1 eventhough case does not have
    # any symptoms
    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/symptoms/1",
            json={"label": "ok"}
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_update_symptom(save, case_data, symptom, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # define current label and updated label
    old_label = "unknown"
    new_label = "defect"
    symptom["label"] = old_label

    # add a single symptom with old label to the case
    data_id = 3
    symptom["data_id"] = data_id
    case_data["symptoms"] = [symptom]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request update of symptom with data_id, which should exist
    with authenticated_client as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/symptoms/{data_id}",
            json={"label": new_label}
        )

    # confirm expected status code and expected new label
    assert response.status_code == 200
    assert response.json()["label"] == new_label
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case.symptoms after saving
    assert Symptom(**response.json()) == saved_cases[0].symptoms[0]


def test_delete_symptom_not_found(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # request deletion of symptom with data_id 1 eventhough case does not have
    # any symptoms
    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/symptoms/1"
        )

    # confirm expected status code (trying to delete a non-existent ressource
    # returns a 200, as desired status is already in place)
    assert response.status_code == 200


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_delete_symptom(save, case_data, symptom, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single symptom to the case
    data_id = 99
    symptom["data_id"] = data_id
    case_data["symptoms"] = [symptom]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request deletion of symptom with data_id, which should exist
    with authenticated_client as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/symptoms/{data_id}"
        )

    # confirm expected status code and non-existence of previously added
    # obd_data
    assert response.status_code == 200
    assert response.json()["symptoms"] == []
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case after saving
    assert Case(**response.json()) == saved_cases[0]


def test_get_diagnosis_no_diag(case_data, authenticated_client):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    authenticated_client.app.dependency_overrides[
        case_from_workshop
    ] = lambda case_id, workshop_id: Case(**case_data)

    with authenticated_client as client:
        response = client.get(f"/{workshop_id}/cases/{case_id}/diag")

    assert response.status_code == 200
    assert response.json() is None


@pytest.fixture
def authenticated_async_client(
        app, rsa_public_key_pem, signed_jwt
):
    """
    Authenticated async client for tests that require mongodb access via beanie
    """

    # Client with valid auth header
    client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://",
        headers={"Authorization": f"Bearer {signed_jwt}"}
    )

    # Make app use public key from fixture for token validation
    app.dependency_overrides[
        Keycloak.get_public_key_for_workshop_realm
    ] = lambda: rsa_public_key_pem.decode()

    return client


@pytest.mark.asyncio
async def test_get_diagnosis(
        case_data, authenticated_async_client, initialized_beanie_context
):
    async with initialized_beanie_context:
        workshop_id = case_data["workshop_id"]
        case_id = case_data["_id"]
        # seed db with diagnosis and associated case
        diag_db_data = {
            "case_id": case_id,
            "state_machine_log": [{"message": "msg", "attachment": None}]
        }
        diag = Diagnosis(**diag_db_data)
        await diag.create()
        case_data["diagnosis_id"] = diag.id
        await Case(**case_data).create()

        # execute test request
        response = await authenticated_async_client.get(
            f"{workshop_id}/cases/{case_id}/diag"
        )

        # confirm expected response data
        assert response.status_code == 200
        diag_response = response.json()
        assert diag_response["case_id"] == case_id
        assert diag_response["state_machine_log"] == diag_db_data[
            "state_machine_log"
        ]


@pytest.mark.asyncio
async def test_start_diagnosis_already_exists(
        case_data, authenticated_async_client, initialized_beanie_context
):
    async with initialized_beanie_context:
        workshop_id = case_data["workshop_id"]
        case_id = case_data["_id"]
        # seed db with diagnosis and associated case
        diag_db_data = {
            "case_id": case_id,
            "state_machine_log": [{"message": "msg", "attachment": None}]
        }
        diag = Diagnosis(**diag_db_data)
        await diag.create()
        case_data["diagnosis_id"] = diag.id
        await Case(**case_data).create()

        # overwrite DiagnosticTaskManager dependency. It should not be called.
        class TestDiagnosticTaskManager:
            async def __call__(self, diagnosis_id):
                raise Exception("This dependency is not expected to be called")

        authenticated_async_client._transport.app.dependency_overrides[
            DiagnosticTaskManager
        ] = TestDiagnosticTaskManager

        # execute test request
        response = await authenticated_async_client.post(
            f"{workshop_id}/cases/{case_id}/diag"
        )

        # confirm expected response data
        assert response.status_code == 201
        diag_response = response.json()
        assert diag_response["case_id"] == case_id
        assert diag_response["state_machine_log"] == diag_db_data[
            "state_machine_log"
        ]


@pytest.mark.asyncio
async def test_start_diagnosis(
        case_data, authenticated_async_client, initialized_beanie_context
):
    async with initialized_beanie_context:
        workshop_id = case_data["workshop_id"]
        case_id = case_data["_id"]
        # seed db with case
        await Case(**case_data).create()

        # overwrite DiagnosticTaskManager dependency
        class TestDiagnosticTaskManager:
            calls = []

            async def __call__(self, diagnosis_id):
                self.calls.append(diagnosis_id)

        authenticated_async_client._transport.app.dependency_overrides[
            DiagnosticTaskManager
        ] = TestDiagnosticTaskManager

        # execute test request
        response = await authenticated_async_client.post(
            f"{workshop_id}/cases/{case_id}/diag"
        )

        # confirm expected response data
        assert response.status_code == 201
        diag_response = response.json()
        assert diag_response["case_id"] == case_id
        assert diag_response["status"] == "scheduled"

        # confirm that diagnosis id was handed over to task manager
        assert TestDiagnosticTaskManager.calls == [
            ObjectId(diag_response["_id"])
        ]

        # confirm expected state in db
        case_db = await Case.get(case_id)
        diag = await Diagnosis.get(diag_response["_id"])
        assert case_db
        assert diag
        assert case_db.diagnosis_id == diag.id


@pytest.mark.asyncio
async def test_delete_diagnosis(
        case_data,
        authenticated_async_client,
        initialized_beanie_context
):
    async with initialized_beanie_context:
        workshop_id = case_data["workshop_id"]
        case_id = case_data["_id"]
        # seed db with diagnosis and associated case
        diag_db_data = {
            "case_id": case_id,
            "state_machine_log": [{"message": "msg", "attachment": None}]
        }
        diag = Diagnosis(**diag_db_data)
        await diag.create()
        case_data["diagnosis_id"] = diag.id
        await Case(**case_data).create()

        # execute test request
        response = await authenticated_async_client.delete(
            f"{workshop_id}/cases/{case_id}/diag"
        )

        # confirm expected response data
        assert response.status_code == 200
        assert response.json() is None

        # confirm expected state in db
        case_db = await Case.get(case_id)
        diag = await Diagnosis.get(diag.id)
        assert case_db
        assert case_db.diagnosis_id is None
        assert diag is None


@pytest.mark.asyncio
async def test_list_diagnoses(
        case_data,
        authenticated_async_client,
        initialized_beanie_context,
        workshop_id
):
    async with initialized_beanie_context:
        # Seed db with 2 cases
        case_1 = await Case(
            workshop_id=workshop_id, vehicle_vin="v11"
        ).insert()
        case_2 = await Case(
            workshop_id=workshop_id, vehicle_vin="v12"
        ).insert()

        # There are no diagnoses, yet
        response = await authenticated_async_client.get(
            f"{workshop_id}/diagnoses"
        )
        assert response.status_code == 200
        assert response.json() == []

        # Add diagnosis for each case
        assert case_1.id
        diag_1 = await Diagnosis(  # noqa F841
            case_id=case_1.id,
            status=DiagnosisStatus("scheduled")
        ).insert()  # noqa F841
        assert case_2.id
        diag_2 = await Diagnosis(
            case_id=case_2.id,
            status=DiagnosisStatus("finished")
        ).insert()

        # There are two diagnoses now
        response = await authenticated_async_client.get(
            f"{workshop_id}/diagnoses"
        )
        assert response.status_code == 200
        assert len(response.json()) == 2, "Expected 2 diagnoses."

        # Only diagnosis 2 has status 'finished'
        response = await authenticated_async_client.get(
            f"{workshop_id}/diagnoses?status=finished"
        )
        assert response.status_code == 200
        assert len(response.json()) == 1, "Expected 1 diagnosis."
        assert response.json()[0]["_id"] == str(diag_2.id)


@pytest.mark.parametrize("route", router.routes, ids=lambda r: r.name)
def test_missing_bearer_token(route, workshop_id, unauthenticated_client):
    """Endpoints should not be accessible without a bearer token."""
    assert len(route.methods) == 1, "Test assumes one method per route."
    path = route.path.replace("{workshop_id}", workshop_id)
    method = next(iter(route.methods))
    response = unauthenticated_client.request(method=method, url=path)
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize("route", router.routes, ids=lambda r: r.name)
def test_unauthorized_workshop(route, authenticated_client):
    """
    Endpoints should not be accessible, if the workshop_id in the path
    does not match the workshop_id encoded in the bearer token.
    """
    assert len(route.methods) == 1, "Test assumes one method per route."
    path = route.path.replace("{workshop_id}", "another workshop id")
    method = next(iter(route.methods))
    response = authenticated_client.request(method=method, url=path)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate token."}


@pytest.mark.parametrize("route", router.routes, ids=lambda r: r.name)
def test_invalid_jwt_signature(
        route, workshop_id, authenticated_client, another_rsa_public_key_pem
):
    """
    Endpoints should not be accessible, if the public key retrieved from
    keycloak does not match the private key used to sign a JWT.
    """
    assert len(route.methods) == 1, "Test assumes one method per route."
    path = route.path.replace("{workshop_id}", workshop_id)
    method = next(iter(route.methods))
    # The token signature of the authenticated client will not match the public
    #  key anymore
    authenticated_client.app.dependency_overrides[
        Keycloak.get_public_key_for_workshop_realm
    ] = lambda: another_rsa_public_key_pem.decode()
    response = authenticated_client.request(method=method, url=path)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate token."}


@pytest.fixture
def expired_jwt_payload(workshop_id):
    return {
        "iat": (datetime.now(UTC) - timedelta(60)).timestamp(),
        "exp": datetime.now(UTC).timestamp(),
        "preferred_username": workshop_id
    }


@pytest.fixture
def expired_jwt(expired_jwt_payload, rsa_private_key_pem: bytes):
    """Create an expired JWT signed with private RSA key."""
    return jws.sign(
        expired_jwt_payload, rsa_private_key_pem, algorithm="RS256"
    )


@pytest.mark.parametrize("route", router.routes, ids=lambda r: r.name)
def test_expired_jwt(route, workshop_id, authenticated_client, expired_jwt):
    """
    Endpoints should not be accessible, if the bearer token is expired.
    """
    assert len(route.methods) == 1, "Test assumes one method per route."
    path = route.path.replace("{workshop_id}", workshop_id)
    method = next(iter(route.methods))
    # The token offered by the authenticated client is expired
    authenticated_client.headers.update(
        {"Authorization": f"Bearer {expired_jwt}"}
    )
    response = authenticated_client.request(method=method, url=path)
    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate token."}
