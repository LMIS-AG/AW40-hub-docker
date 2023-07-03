from typing import Union, Tuple

import keras
from vehicle_diag_smach.interfaces.model_accessor import ModelAccessor


class HubModelAccessor(ModelAccessor):

    def get_keras_univariate_ts_classification_model_by_component(
            self, component: str
    ) -> Union[Tuple[keras.models.Model, dict], None]:
        return None
