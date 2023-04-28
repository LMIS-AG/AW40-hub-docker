import codecs
import csv
import re
from typing import BinaryIO, List

from ..filereader import FileReader

conv_table = {
    "(s)": 1e0,
    "(ms)": 1e-3,
    "(μs)": 1e-6,
    "(V)": 1e0,
    "(mV)": 1e-3,
    "(μV)": 1e-6
}

HEADER_CHECK = re.compile(r"^Time(?:,Channel [A-Z])+$")
CONVHEADER_CHECK = re.compile(
    r"^\((?:m|μ){0,1}(?:s|V)\)(?:,\((?:m|μ){0,1}(?:s|V)\))+$")


class PicoscopeCSVReader(FileReader):
    def read_file(self, file: BinaryIO) -> List[dict]:
        result = []
        if not self.__probe(file):
            raise Exception("conversion failed: wrong format")
        data = self.__csv_to_dict(file)
        duration = self.__calculate_duration(data)
        sampling_rate = self.__calculate_sampling_rate(data)[0]
        for key in data.keys():
            if key.startswith('Channel'):
                result.append({
                    'duration': duration,
                    'sampling_rate': sampling_rate,
                    'signal': data[key],
                    'device_specs': {
                        "channel": key.replace('Channel ', ''),
                        "type": "picoscope"
                    }
                })
        return result

    def __probe(self, file):
        file_iter = codecs.iterdecode(file, "utf-8")
        header = next(file_iter).strip()
        conv_header = next(file_iter).strip()
        validated = HEADER_CHECK.match(header) and CONVHEADER_CHECK.match(conv_header)
        file.seek(0)
        return validated

    def __csv_to_dict(self, file):
        reader = csv.reader(codecs.iterdecode(file, 'utf-8'))
        header = next(reader)
        data = {}
        conversion = []

        for column in header:
            data[column] = []

        for type in next(reader):
            conversion.append(conv_table[type])

        for row in reader:
            if len(row) > 0 and len(row) != len(header):
                raise Exception("conversion failed: discontinuity detected")
            for count, element in enumerate(row):
                try:
                    data[header[count]].append(
                        float(element) * conversion[count])
                except Exception as e:
                    raise Exception("conversion failed:{}".format(str(e)))
        return data

    def __calculate_duration(self, data):
        return abs(data['Time'][0]) + data['Time'][-1]

    def __calculate_sampling_rate(self, data):
        sr_arr = []
        last = 0
        for cnt, ent in enumerate(data['Time']):
            if cnt > 0:
                # Check aroung Time 0 since Picoscope start with negative time
                if last < 0 and ent >= 0:
                    sr_arr.append(1.0 / (abs(abs(last) + abs(ent))))
                else:
                    sr_arr.append(1.0 / (abs(abs(last) - abs(ent))))
            last = ent
        sr = (sum(sr_arr) / len(sr_arr))
        return sr, min(sr_arr) - sr, max(sr_arr) - sr
