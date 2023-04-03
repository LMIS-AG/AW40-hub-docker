from collections import namedtuple
from unittest import mock

import pytest
from api.data_management import (
    Case,
    Vehicle,
    Customer,
    Workshop,
    TimeseriesData,
    NewTimeseriesData,
    OBDData,
    Symptom
)
from api.routers.workshop import router, case_from_workshop
from beanie import init_beanie
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient


@pytest.fixture
def case_id():
    """Valid case_id, e.g. needs to work with PydanticObjectId"""
    return "5eb7cf5a86d9755df3a6c593"


@pytest.fixture
def case_data(case_id):
    """Valid (minimal) case data."""
    return {
        "_id": case_id,
        "vehicle_vin": "test-vin",
        "workshop_id": "test-workshop",
    }


@pytest.fixture
def obd_data():
    """Valid obd data."""
    return {"dtcs": ["P0001", "U0001"]}


@pytest.fixture
def symptom():
    """Valid symptom data."""
    return {"component": "Batterie", "label": "defekt"}


@pytest.fixture
def test_app(motor_db):
    """
    Request this fixture to test routes via TestClient(test_app) as described
    in https://fastapi.tiangolo.com/tutorial/testing/.
    If a test requires beanie initialization, (e.g. because a non-mock
    instance of a beanie doc is created at some point) this fixture needs to
    be used in a with statement (e.g. with TestClient(test_app) as client: ...)
    Using a with statement ensures execution of the test applications startup
    and shutdown handlers used for beanie/mongo setup and teardown
    (see https://fastapi.tiangolo.com/advanced/testing-events/).
    """
    test_app = FastAPI()
    test_app.include_router(router)

    models = [Case, Vehicle, Customer, Workshop]

    @test_app.on_event("startup")
    async def init_mongo():
        await init_beanie(
            motor_db,
            document_models=[Case, Vehicle, Customer, Workshop]
        )
        for model in models:
            # make sure all collections are empty at the beginning of each
            # test
            await model.delete_all()

    @test_app.on_event("shutdown")
    async def teardown_mongo():
        for model in models:
            await model.get_motor_collection().drop()
            await model.get_motor_collection().drop_indexes()

    yield test_app


@pytest.fixture
def client(test_app):
    """
    Convenience fixture. Can be used in tests that do not require
    modification of the test_app fixture.
    """
    yield TestClient(test_app)


@mock.patch("api.routers.workshop.Case.find_in_hub", autospec=True)
def test_list_cases(find_in_hub, client):
    workshop_id = "test workshop"

    async def mock_find_in_hub(customer_id, workshop_id, vin):
        return []

    # patch Case.find_in_hub to use mock_find_in_hub
    find_in_hub.side_effect = mock_find_in_hub

    # request without params
    response = client.get(f"/{workshop_id}/cases")

    # confirm expected response and usage of db interface
    assert response.status_code == 200
    assert response.json() == []
    find_in_hub.assert_called_once_with(
        customer_id=None, vin=None, workshop_id=workshop_id
    )


@mock.patch("api.routers.workshop.Case.find_in_hub", autospec=True)
def test_list_cases_with_filters(find_in_hub, client):
    workshop_id = "test workshop"

    async def mock_find_in_hub(customer_id, workshop_id, vin):
        return []

    # patch Case.find_in_hub to use mock_find_in_hub
    find_in_hub.side_effect = mock_find_in_hub

    # request with filter params
    customer_id = "test customer"
    vin = "test vin"
    response = client.get(
        f"/{workshop_id}/cases",
        params={"customer_id": customer_id, "vin": vin}
    )

    # confirm expected response and usage of db interface
    assert response.status_code == 200
    assert response.json() == []
    find_in_hub.assert_called_once_with(
        customer_id=customer_id, vin=vin, workshop_id=workshop_id
    )


def test_add_case(client):
    workshop_id = "test workshop"
    new_case = {
        "vehicle_vin": "test-vin",
        "customer_id": "test.customer",
        "occasion": "keine Angabe",
        "milage": 42
    }
    with client:
        response = client.post(f"/{workshop_id}/cases", json=new_case)

    assert response.status_code == 201
    assert response.json()["_id"] is not None


@mock.patch("api.routers.workshop.Case.get", autospec=True)
@pytest.mark.asyncio
async def test_case_from_workshop(get):
    case_id = "test case"
    workshop_id = "test workshop"

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
async def test_case_from_workshop_is_none(get):

    async def mock_get(*args):
        """Always returns None, e.g. no case found."""
        return None

    # patch Case.get to use mock_get instead
    get.side_effect = mock_get

    # since there is no case, a 404 should be raised
    with pytest.raises(HTTPException) as excinfo:
        await case_from_workshop(workshop_id="anything", case_id="anything")
    assert excinfo.value.status_code == 404


@mock.patch("api.routers.workshop.Case.get", autospec=True)
@pytest.mark.asyncio
async def test_case_from_workshop_wrong_workshop(get):
    case_id = "test case"
    workshop_id = "test workshop"

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


def test_get_case(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}"
        )

    # confirm expected status code and response schema
    assert response.status_code == 200
    assert Case(**response.json())


@mock.patch("api.routers.workshop.Case.set", autospec=True)
def test_update_case(case_set, case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    case_data["status"] = "offen"
    new_status = "abgeschlossen"

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.set with AsyncMock to confirm use with await
    case_set.side_effect = mock.AsyncMock()

    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}",
            json={"status": new_status}
        )

    # confirm expected status code and response schema
    assert response.status_code == 200
    assert Case(**response.json())

    # confirm await of Case.set
    case_set.side_effect.assert_awaited_once()


def test_delete_case(case_data, test_app):

    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    with TestClient(test_app) as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}"
        )
    assert response.status_code == 200


def test_list_timeseries_data(case_data, timeseries_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add timeseries_data multiple times to case_data
    repeats = 2
    case_data["timeseries_data"] = repeats*[timeseries_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data"
        )

    # confirm expected status code and response shape
    assert response.status_code == 200
    assert len(response.json()) == repeats


@mock.patch("api.routers.workshop.Case.add_timeseries_data", autospec=True)
def test_add_timeseries_data(
        add_timeseries_data,
        case_data,
        new_timeseries_data,
        test_app,
        timeseries_signal_id
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    async def mock_add_timeseries_data(self, new_data: NewTimeseriesData):
        # exchange signal and signal_id without accessing signal store
        signal_id = timeseries_signal_id
        meta_data = new_data.dict(exclude={"signal"})
        meta_data["signal_id"] = signal_id
        timeseries_data = TimeseriesData(**meta_data)

        # append to case without saving
        self.timeseries_data.append(timeseries_data)
        return self

    # patch Case.add_timeseries_data to use mock_add_timeseries_data
    add_timeseries_data.side_effect = mock_add_timeseries_data

    with TestClient(test_app) as client:
        response = client.post(
            f"/{workshop_id}/cases/{case_id}/timeseries_data",
            json=new_timeseries_data
        )

    # confirm expected status code and response shape
    assert response.status_code == 201
    assert len(response.json()["timeseries_data"]) == 1


def test_get_timeseries_data_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request timeseries_data with data_id 1 eventhough case does not have
    # any timeseries data
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1"
        )

    # confirm expected status code
    assert response.status_code == 404


def test_get_timeseries_data(case_data, timeseries_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single timeseries data set to the case
    case_data["timeseries_data"] = [timeseries_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request timeseries_data with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/0"
        )

    # confirm expected status code and response shema
    assert response.status_code == 200
    assert TimeseriesData(**response.json())


def test_get_timeseries_data_signal_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request signal from timeseries_data with data_id 1 eventhough case does
    # not have any timeseries data
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1/signal"
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.TimeseriesData.get_signal", autospec=True)
def test_get_timeseries_data_signal(
        get_signal, case_data, timeseries_data, test_app
):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single timeseries data set to the case
    case_data["timeseries_data"] = [timeseries_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    test_signal = [0., 1., 2.]

    async def mock_get_signal(self):
        return test_signal

    # patch Case.get_signal to use mock_get_signal
    get_signal.side_effect = mock_get_signal

    # request signal from timeseries_data with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/0/signal"
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


def test_update_timeseries_data_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request update of timeseries_data with data_id 1 eventhough case does not
    # have any timeseries data
    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/1",
            json={"label": "Regelfall / Unauffällig"}
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_update_timeseries_data(save, case_data, timeseries_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # define current label and updated label
    old_label = "keine Angabe"
    new_label = "Regelfall / Unauffällig"
    timeseries_data["label"] = old_label

    # add a single timeseries_data with old label to the case
    case_data["timeseries_data"] = [timeseries_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request update of timeseries_data with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/timeseries_data/0",
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


def test_list_obd_data(case_data, obd_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add obd_data multiple times to case_data
    repeats = 2
    case_data["obd_data"] = repeats*[obd_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/obd_data"
        )

    # confirm expected status code and response shape
    assert response.status_code == 200
    assert len(response.json()) == repeats


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_add_obd_data(save, case_data, obd_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    with TestClient(test_app) as client:
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


def test_get_obd_data_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request obd_data with data_id 1 eventhough case does not have
    # any obd data
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/obd_data/1"
        )

    # confirm expected status code
    assert response.status_code == 404


def test_get_obd_data(case_data, obd_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single obd data set to the case
    case_data["obd_data"] = [obd_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request obd_data with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/obd_data/0"
        )

    # confirm expected status code and response shema
    assert response.status_code == 200
    assert OBDData(**response.json())


def test_update_obd_data_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request update of obd_data with data_id 1 eventhough case does not have
    # any obd data
    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/obd_data/1",
            json={"obd_specs": {"some field": "some value"}}
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_update_obd_data(save, case_data, obd_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    old_obd_specs = {"device": "vcds 123"}
    new_obd_specs = {"device": "VCDS"}
    obd_data["obd_specs"] = old_obd_specs

    # add a single obd data set to the case
    case_data["obd_data"] = [obd_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request update of obd_data with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/obd_data/0",
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


def test_delete_obd_data_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request deletion of obd_data with data_id 1 eventhough case does not have
    # any obd data
    with TestClient(test_app) as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/obd_data/1"
        )

    # confirm expected status code (trying to delete a non-existent ressource
    # returns a 200, as desired status is already in place)
    assert response.status_code == 200


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_delete_obd_data(save, case_data, obd_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single obd data set to the case
    case_data["obd_data"] = [obd_data]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request deletion of obd_data with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/obd_data/0"
        )

    # confirm expected status code and non-existence of previously added
    # obd_data
    assert response.status_code == 200
    assert response.json()["obd_data"] == [None]
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case after saving
    assert Case(**response.json()) == saved_cases[0]


def test_list_symptoms(case_data, symptom, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add symptom multiple times to case_data
    repeats = 2
    case_data["symptoms"] = repeats*[symptom]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/symptoms"
        )

    # confirm expected status code and response shape
    assert response.status_code == 200
    assert len(response.json()) == repeats


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_add_symptom(save, case_data, symptom, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    with TestClient(test_app) as client:
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


def test_get_symptom_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request symptom with data_id 1 eventhough case does not have
    # any symptoms
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/symptoms/1"
        )

    # confirm expected status code
    assert response.status_code == 404


def test_get_symptom(case_data, symptom, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single symptom to the case
    case_data["symptoms"] = [symptom]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request symptom with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.get(
            f"/{workshop_id}/cases/{case_id}/symptoms/0"
        )

    # confirm expected status code and response shema
    assert response.status_code == 200
    assert Symptom(**response.json())


def test_update_symptom_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request update of symptom with data_id 1 eventhough case does not have
    # any symptoms
    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/symptoms/1",
            json={"label": "nicht defekt"}
        )

    # confirm expected status code
    assert response.status_code == 404


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_update_symptom(save, case_data, symptom, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # define current label and updated label
    old_label = "keine Angabe"
    new_label = "defekt"
    symptom["label"] = old_label

    # add a single symptom with old label to the case
    case_data["symptoms"] = [symptom]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request update of symptom with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.put(
            f"/{workshop_id}/cases/{case_id}/symptoms/0",
            json={"label": new_label}
        )

    # confirm expected status code and expected new label
    assert response.status_code == 200
    assert response.json()["label"] == new_label
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case.symptoms after saving
    assert Symptom(**response.json()) == saved_cases[0].symptoms[0]


def test_delete_symptom_not_found(case_data, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # request deletion of symptom with data_id 1 eventhough case does not have
    # any symptoms
    with TestClient(test_app) as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/symptoms/1"
        )

    # confirm expected status code (trying to delete a non-existent ressource
    # returns a 200, as desired status is already in place)
    assert response.status_code == 200


@mock.patch("api.routers.workshop.Case.save", autospec=True)
def test_delete_symptom(save, case_data, symptom, test_app):
    workshop_id = case_data["workshop_id"]
    case_id = case_data["_id"]

    # add a single symptom to the case
    case_data["symptoms"] = [symptom]

    test_app.dependency_overrides = {
        case_from_workshop: lambda case_id, workshop_id: Case(**case_data)
    }

    # patch Case.save to use mock_save
    mock_save, saved_cases = create_mock_save()
    save.side_effect = mock_save

    # request deletion of symptom with data_id 0, which should exist
    with TestClient(test_app) as client:
        response = client.delete(
            f"/{workshop_id}/cases/{case_id}/symptoms/0"
        )

    # confirm expected status code and non-existence of previously added
    # obd_data
    assert response.status_code == 200
    assert response.json()["symptoms"] == [None]
    # confirm case was saved
    assert len(saved_cases) == 1
    # confirm response data represents case after saving
    assert Case(**response.json()) == saved_cases[0]
