from typing import List

from PIL.Image import Image
from vehicle_diag_smach.data_types.state_transition import StateTransition
from vehicle_diag_smach.interfaces.data_provider import DataProvider

from ..hub_client import HubClient


class HubDataProvider(DataProvider):

    def __init__(self, hub_client: HubClient):
        self.hub_client = hub_client

    def _log(self, message):
        self.hub_client.add_to_state_machine_log(message)

    def provide_causal_graph_visualizations(
            self, visualizations: List[Image]
    ) -> None:
        self._log("visualizations: ")

    def provide_heatmaps(self, heatmaps: Image, title: str) -> None:
        self._log(f"heatmaps: title: {title}")

    def provide_diagnosis(self, fault_paths: List[str]) -> None:
        self._log(f"fault_paths: {fault_paths}")

    def provide_state_transition(
            self, state_transition: StateTransition
    ) -> None:
        self._log(f"state_transition: {str(state_transition)}")
