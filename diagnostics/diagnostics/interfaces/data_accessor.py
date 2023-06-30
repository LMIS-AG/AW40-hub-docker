from typing import List, Union

from vehicle_diag_smach.data_types.customer_complaint_data import (
    CustomerComplaintData
)
from vehicle_diag_smach.data_types.onboard_diagnosis_data import (
    OnboardDiagnosisData
)
from vehicle_diag_smach.data_types.oscillogram_data import OscillogramData
from vehicle_diag_smach.data_types.workshop_data import WorkshopData
from vehicle_diag_smach.interfaces.data_accessor import DataAccessor

from ..hub_client import HubClient


class InsufficientDataException(Exception):
    pass


class MissingOBDDataException(InsufficientDataException):
    pass


class MissingOscillogramsException(InsufficientDataException):
    def __init__(self, message, components):
        super().__init__(message)
        self.components = components


class HubDataAccessor(DataAccessor):

    def __init__(self, hub_client: HubClient):
        self.hub_client = hub_client

    def get_workshop_info(self) -> WorkshopData:
        diag = self.hub_client.get_diag()
        return WorkshopData(
            num_of_parallel_rec=1,
            diag_date=diag["timestamp"]
        )

    def _get_dtcs(self) -> List[str]:
        hub_obd_data = self.hub_client.get_obd_data()
        if len(hub_obd_data) == 0:
            return None
        elif len(hub_obd_data) == 1:
            return hub_obd_data[0]["dtcs"]
        else:
            raise ValueError(
                "Case contains more than one OBD Dataset. "
                "This cannot be handled yet"
            )

    def get_obd_data(self) -> OnboardDiagnosisData:
        dtcs = self._get_dtcs()
        if not dtcs:
            raise MissingOBDDataException

        vehicle = self.hub_client.get_vehicle()
        return OnboardDiagnosisData(
            dtc_list=dtcs,
            model=vehicle.get("model"),
            hsn=vehicle.get("hsn", ""),
            tsn=vehicle.get("tsn"),
            vin=vehicle.get("vin")
        )

    def _get_oscillogram_by_component(
            self, component: str
    ) -> Union[None, OscillogramData]:
        signals = self.hub_client.get_oscillograms(component=component)
        if len(signals) == 0:
            return None
        elif len(signals) == 1:
            return OscillogramData(
                time_series=signals[0],
                comp_name=component
            )
        else:
            raise ValueError(
                f"Got more than one Oscillogram for "
                f"component {component}. This cannot be handled yet."
            )

    def get_oscillograms_by_components(
            self, components: List[str]
    ) -> OscillogramData:
        oscillograms = []
        missing_components = []
        for component in components:
            oscillograms.append(
                self._get_oscillogram_by_component(component)
            )
            if oscillograms[-1] is None:
                missing_components.append(component)

        if len(missing_components) > 0:
            message = f"Failed to retrieve oscillograms for components: " \
                      f"{missing_components}"
            raise MissingOscillogramsException(message, missing_components)

        return oscillograms

    def get_customer_complaints(self) -> CustomerComplaintData:
        return CustomerComplaintData()

    def get_manual_judgement_for_component(self, component: str) -> bool:
        return False

    def get_manual_judgement_for_sensor(self) -> bool:
        return False
