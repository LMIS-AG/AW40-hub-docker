from abc import ABC
from typing import BinaryIO, List


class FileReader(ABC):
    def read_file(self, file: BinaryIO) -> List[dict]:
        raise NotImplementedError
