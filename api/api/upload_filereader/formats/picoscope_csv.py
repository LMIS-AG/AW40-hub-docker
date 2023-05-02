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

#channel_names = [
#    "Kanal",
#    "Channel"
#]

time_names = [
    "Zeit",
    "Time"
]

#HEADER_CHECK = re.compile(r"^(?:Time|Zeit)(?:,(?:Channel|Kanal) [A-Z])+$")
HEADER_CHECK = re.compile(
    r"^\w*(?P<delimiter>[,;])(?:\w* [A-Z])(?:\1\w* [A-Z])*$")
CONVHEADER_CHECK = re.compile(
    r"^\((?:m|μ){0,1}(?:s|V)\)(?:[,;]\((?:m|μ){0,1}(?:s|V)\))+$")
ALLOWED_CHANNEL = re.compile(r"[A-Z]")
CHANNEL_CHECK = re.compile(r"^(?P<channel_name>\w*) (?P<channel>[A-Z])$")


class PicoscopeCSVReader(FileReader):
    def read_file(self, file: BinaryIO) -> List[dict]:
        result = []
        validated, delimiter =  self.__probe(file)
        if not validated:
            raise Exception("conversion failed: wrong format")
        data = self.__csv_to_dict(file, delimiter)
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
    
    def __translate_header(self, header):
        translated = []
        for item in header:
            if item in time_names:
                translated.append("Time")
            else:
                channel_check = CHANNEL_CHECK.match(item)
                if channel_check:
                    channel = channel_check["channel"]
                    translated.append("Channel {}".format(channel))
        if len(translated) != len(header):
            raise Exception("conversion failed: failed to translate header")
        return translated

    def __probe(self, file):
        delimiter = ""
        validated = False
        file_iter = codecs.iterdecode(file, "utf-8")
        header = next(file_iter).strip()
        conv_header = next(file_iter).strip()
        header_check = HEADER_CHECK.match(header)
        conv_header_check = CONVHEADER_CHECK.match(conv_header)
        if header_check and conv_header_check:
            delimiter = header_check["delimiter"]
            validated = True
        file.seek(0)
        return validated, delimiter

    def __csv_to_dict(self, file, delimiter):
        reader = csv.reader(codecs.iterdecode(file, 'utf-8'),
                            delimiter=delimiter)
        header = self.__translate_header(next(reader))
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
