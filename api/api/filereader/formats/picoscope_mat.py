from filereader import filereader
from scipy.io import loadmat

class picoscope_mat_reader(filereader):
    def read_file(self, path):
        measuement = self.__read_mat(path)
        return measuement
    
    def probe(self,path):
        return path.endswith(".mat")
    
    def __read_mat(self, path):
        f = loadmat(path)
        result = {
            'timeseries_data' : []
        }
        if 'Tinterval' not in f.keys():
            raise Exception("conversion error: missing Tinterval")
        if 'Length' not in f.keys():
            raise Exception("conversion error: missing Length")
        sampling_rate = 1.0/f['Tinterval'].item(0)
        duration = f['Tinterval'].item(0) * f['Length'].item(0)
        channels = [x for x in f.keys() if len(x) == 1]
        if len(channels) == 0:
            raise Exception("conversion error: no channels found")
        for channel in channels:
            result['timeseries_data'].append({
                'sampling_rate' : sampling_rate,
                'duration' : duration,
                'signal_data': f[channel].ravel(),
                'component': channel
            })
        return result