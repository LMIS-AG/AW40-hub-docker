from .storage import Storage
from .storages.storages import SUPPORTED_STORAGES


class StorageFactory():
    config = dict()

    def get_storage(self, Name: str) -> Storage:
        cfg = self.config[Name]
        constructor = SUPPORTED_STORAGES[Name]
        return constructor(**cfg)


def initialise_storages(**kwargs):
    for name in SUPPORTED_STORAGES.keys():
        prefix = f"{name.lower()}_"
        args = {k.removeprefix(prefix): v for (k, v) in kwargs.items()
                if k.startswith(prefix)}
        StorageFactory.config[name] = args
