import pytest
from api.data_management import (
    NewCase,
    Case,
    Vehicle,
    Customer,
    Workshop,
    NewTimeseriesData,
    TimeseriesData
)
from beanie import init_beanie
from pydantic import ValidationError


@pytest.fixture
def new_case():
    """Valid meta data for a new case"""
    return {
        "vehicle_vin": "test-vin",
        "customer_id": "test.customer",
        "occasion": "keine Angabe",
        "milage": 42
    }


class TestNewCase:

    def test_validation_fails_without_vin(self, new_case):
        with pytest.raises(ValidationError):
            new_case.pop("vehicle_vin")
            NewCase(**new_case)

    def test_default_input(self):
        # only vin required, everything else has default values
        NewCase(vehicle_vin="123")

    def test_non_default_input(self, new_case):
        NewCase(**new_case)


@pytest.fixture
def initialized_beanie_context(motor_db):
    """
    Could not get standard pytest fixture setup and teardown to work for
    beanie initialization. As a workaround this fixture creates an async
    context manager to handle test setup and teardown.
    """
    models = [
        Case,
        Vehicle,
        Customer,
        Workshop
    ]

    class InitializedBeanieContext:
        async def __aenter__(self):
            await init_beanie(
                motor_db,
                document_models=models
            )
            for model in models:
                # make sure all collections are empty at the beginning of each
                # test
                await model.delete_all()

        async def __aexit__(self, exc_type, exc, tb):
            for model in models:
                # drop all collections and indexes after each test
                await model.get_motor_collection().drop()
                await model.get_motor_collection().drop_indexes()

    return InitializedBeanieContext()


class TestCase:

    @pytest.mark.asyncio
    async def test_validation_fails_without_workshop_id(
            self, new_case, initialized_beanie_context
    ):
        async with initialized_beanie_context:
            with pytest.raises(ValidationError):
                Case(**new_case)

    @pytest.mark.asyncio
    async def test_validation_with_workshop_id(
            self, new_case, initialized_beanie_context
    ):
        async with initialized_beanie_context:
            Case(workshop_id=1, **new_case)

    @pytest.mark.asyncio
    async def test_automatic_vehicle_insert(
            self, new_case, initialized_beanie_context
    ):
        async with initialized_beanie_context:
            # assert no vehicles yet
            all_vehicles = await Vehicle.find_all().to_list()
            assert len(all_vehicles) == 0

            # create a new case
            new_vin = new_case["vehicle_vin"]
            case = Case(workshop_id=1, **new_case)
            await case.create()

            # assert vehicle was created automatically
            all_vehicles = await Vehicle.find_all().to_list()
            assert len(all_vehicles) == 1
            created_vehicle = all_vehicles[0]
            assert created_vehicle.vin == new_vin

    @pytest.mark.asyncio
    async def test_automatic_customer_insert(
            self, new_case, initialized_beanie_context
    ):
        async with initialized_beanie_context:
            # assert no customers yet
            all_customers = await Customer.find_all().to_list()
            assert len(all_customers) == 0

            # create a new case
            new_customer_id = new_case["customer_id"]
            case = Case(workshop_id=1, **new_case)
            await case.create()

            # assert customer was created automatically
            all_customers = await Customer.find_all().to_list()
            assert len(all_customers) == 1
            created_customer = all_customers[0]
            assert created_customer.id == new_customer_id

    @pytest.mark.asyncio
    async def test_find_in_hub_default(
            self, new_case, initialized_beanie_context
    ):
        async with initialized_beanie_context:
            # no cases yet, empty list expected
            all_cases = await Case.find_in_hub()
            assert len(all_cases) == 0

            # insert a case
            await Case(workshop_id=1, **new_case).create()

            # find_in_hub without args should work and return all cases
            all_cases = await Case.find_in_hub()
            assert len(all_cases) == 1

    @pytest.mark.asyncio
    async def test_find_in_hub(
            self, new_case, initialized_beanie_context
    ):
        async with initialized_beanie_context:
            # three cases are identical at the beginning
            new_case["workshop_id"] = 1
            case_1 = dict(**new_case)
            case_2 = dict(**new_case)
            case_3 = dict(**new_case)

            # alter customer for case 1 and create
            case_1_customer_id = "Case 1 Customer"
            case_1["customer_id"] = case_1_customer_id
            case_1 = Case(**case_1)
            await case_1.create()

            # alter vin for case 2 and create
            case_2_vin = "Case 2 VIN"
            case_2["vehicle_vin"] = case_2_vin
            case_2 = Case(**case_2)
            await case_2.create()

            # alter workshop for case 3 and create
            case_3_workshop_id = "Case 3 Workshop ID"
            case_3["workshop_id"] = case_3_workshop_id
            case_3 = Case(**case_3)
            await case_3.create()

            # filter condition should only match case 1
            case_1_result = await Case.find_in_hub(
                customer_id=case_1_customer_id
            )
            # filter condition should only match case 2
            case_2_result = await Case.find_in_hub(
                vin=case_2_vin
            )
            # filter condition should only match case 3
            case_3_result = await Case.find_in_hub(
                workshop_id=case_3_workshop_id
            )

            # single case expected for each filter condition
            assert len(case_1_result) == 1
            assert len(case_2_result) == 1
            assert len(case_3_result) == 1

            # confirm expected data
            assert case_1_result[0].customer_id == case_1_customer_id
            assert case_2_result[0].vehicle_vin == case_2_vin
            assert case_3_result[0].workshop_id == case_3_workshop_id

    @pytest.mark.asyncio
    async def test_add_timeseries_data(
            self, new_case, initialized_beanie_context, monkeypatch
    ):

        test_signal_id = "5eb7cf5a86d9755df3a6c593"

        new_timeseries_data = {
            "component": "Batterie",
            "label": "keine Angabe",
            "sampling_rate": 1,
            "duration": 2,
            "type": "oscillogram",
            "signal": [42., 99.]
        }

        class MockNewTimeseriesData(NewTimeseriesData):
            """
            A mock for NewTimeseriesData that does not interact with a
            signal store when executing to_timeseries_data.
            """
            async def to_timeseries_data(self):
                signal_id = test_signal_id
                meta_data = self.dict(exclude={"signal"})
                meta_data["signal_id"] = signal_id
                return TimeseriesData(**meta_data)

        async with initialized_beanie_context:
            case = Case(workshop_id=1, **new_case)

            # Case.add_timeseries_data calls arguments .to_timeseries_data
            # method. Hence, pass instance of the mock class, to avoid
            # configuration of a signal store backend
            new_data = MockNewTimeseriesData(**new_timeseries_data)
            await case.add_timeseries_data(new_data)

            # refetch case and assert existence of single timeseries with
            # expected signal_id
            case_retrieved = await Case.get(case.id)
            assert len(case_retrieved.timeseries_data) == 1
            timeseries_data_retrieved = case_retrieved.timeseries_data[0]
            assert str(timeseries_data_retrieved.signal_id) == test_signal_id
