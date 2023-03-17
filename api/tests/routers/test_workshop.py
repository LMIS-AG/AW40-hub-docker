from collections import namedtuple
from unittest import mock

import pytest
from api.routers.workshop import router, case_from_workshop
from fastapi import HTTPException
from fastapi.testclient import TestClient

client = TestClient(router)


@mock.patch("api.routers.workshop.Case.find_in_hub", autospec=True)
def test_list_cases(find_in_hub):
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
def test_list_cases_with_filters(find_in_hub):
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
