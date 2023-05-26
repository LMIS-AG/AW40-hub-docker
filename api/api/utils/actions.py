from ..data_management import Component


def _create_action_add_oscillogram(component):
    return {
        "id": f"add-data-oscillogram-{component.lower()}",
        "instruction": f"Bitte ein Oszillogramm für das Bauteil '{component}' "
                       f"erstellen und hochladen.",
        "action_type": "add_data",
        "data_type": "oscillogram",
        "component": f"{component}"
    }


def _create_action_add_obd():
    return {
        "id": "add-data-obd",
        "instruction": "Bitte OBD Daten erstellen und hochladen.",
        "action_type": "add_data",
        "data_type": "obd",
    }


def create_action_data():
    all_actions = [
        _create_action_add_obd(),
        *[_create_action_add_oscillogram(x.value) for x in Component]

    ]
    return all_actions
