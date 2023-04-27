import numpy as np
from filereader import filereader

class omniscope_v1_reader:
    def read_file(self, path):
        result = {
            'timeseries_data' : []
        }
        data = []
        with open(path, 'rb') as f:
            while True:
                b = f.read(2)
                if b:
                    ADC_value = int.from_bytes(b, "little") & 0xFFF
                    volt = int((ADC_value - 1551) * 8.05860805860806) / 1000.0
                    data.append(volt)
                else:
                    result['timeseries_data'].append({
                        'signal_data': np.asarray(data, dtype=np.float32),
                        'component' : 'A'
                        })
                    break
        return result
    
    def probe(self, path):
        #Cannot guess RAW Data return False as default
        return False