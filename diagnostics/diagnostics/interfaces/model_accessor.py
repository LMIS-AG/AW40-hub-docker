from typing import Union

import keras
from vehicle_diag_smach.interfaces.model_accessor import ModelAccessor


class HubModelAccessor(ModelAccessor):

    def get_model_by_component(
            self, component: str
    ) -> Union[keras.models.Model, None]:
        return None
