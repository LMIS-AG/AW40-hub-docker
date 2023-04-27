import csv
import re
import numpy as np
from filereader import filereader

conv_table = {
    "(s)": 1e0,
    "(ms)": 1e-3,
    "(μs)": 1e-6,
    "(V)": 1e0,
    "(mV)": 1e-3,
    "(μV)": 1e-6
}

HEADER_CHECK = re.compile(r"^Time(?:,Channel [A-Z])+$")
CONVHEADER_CHECK = re.compile(r"^\((?:m|μ){0,1}(?:s|V)\)(?:,\((?:m|μ){0,1}(?:s|V)\))+$")

class picoscope_csv_reader(filereader):
    def read_file(self, path):
        result = {
            'timeseries_data' : []
        }
        if not self.probe(path):
            raise Exception("conversion failed: wrong format")
        data = self.__csv_to_dict(path)
        duration = self.__calculate_duration(data)
        sampling_rate = self.__calculate_sampling_rate(data)[0]
        for key in data.keys():
            if key.startswith('Channel'):
                result['timeseries_data'].append({
                    'duration': duration,
                    'sampling_rate': sampling_rate,
                    'signal_data' :  np.asarray(data[key], dtype=np.float32),
                    'component' : key.replace('Channel ','')
                })
        return result
    
    def probe(self, path):
        if not path.endswith(".csv"):
            return False
        with open(path, newline='') as f:
            header = f.readline()
            conv_header = f.readline()
            if HEADER_CHECK.match(header) and CONVHEADER_CHECK.match(conv_header):
                return True
        return False
    
    def __csv_to_dict(self, path):
        with open(path, newline='') as f:
            reader = csv.reader(f)
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
                        data[header[count]].append(float(element)*conversion[count])
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
                        sr_arr.append(1.0/(abs(abs(last)+abs(ent))))
                    else:
                        sr_arr.append(1.0/(abs(abs(last)-abs(ent))))
                last = ent
            sr = (sum(sr_arr)/len(sr_arr))
            return sr, min(sr_arr) - sr, max(sr_arr) - sr