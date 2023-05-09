from typing import BinaryIO, List

from ..filereader import FileReader


class OmniscopeV1Reader(FileReader):
    def read_file(self, file: BinaryIO) -> List[dict]:
        data = []
        result = {"device_specs": {"type": "omniscope v1"}}
        while True:
            b = file.read(2)
            if b:
                ADC_value = int.from_bytes(b, "little") & 0xFFF
                volt = int((ADC_value - 1551) * 8.05860805860806) / 1000.0
                data.append(volt)
            else:
                result["signal"] = data
                break
        # all file readers return a list
        result = [result]
        return result
