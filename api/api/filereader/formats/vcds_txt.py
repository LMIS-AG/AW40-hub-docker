import re
import chardet
from filereader import filereader
import logging as log

OBD_ERROR = re.compile(r"^\s*(?P<error_code>[BCPU][01][0-7][0-9A-Z]{2}) \d{2} \[\d{3}\] - (?P<error_string>.*)$")
VIN_AND_MILAGE = re.compile(r"^Fahrzeug-Ident\.-Nr\.: (?P<vin>[A-HJ-NPR-Za-hj-npr-z0-9]{17})\s*Kilometerstand: (?P<milage>\d+)km")
VCDS_INFO = re.compile(r"^\s*VCDS Version: DRV (?P<driver_version>[0-9A-Fa-f.]+)  HEX-V2 CB: (?P<hex_v2>[0-9A-Fa-f.]+)\s*$")

class vcds_txt_reader(filereader):
    def read_file(self, path):
        enc = self.__determine_encoding(path)
        return self.__read_vcds_txt(path, enc)
    
    def probe(self, path):
        if not path.endswith(".txt"):
            return False
        enc = self.__determine_encoding(path)
        if self.__get_obd_specs(path, enc):
            return True
        return False
    
    def __get_obd_specs(self, path, enc):
        with open(path,'r',encoding=enc) as f:
            for _ in range(0,6):
                vcds_info = VCDS_INFO.match(f.readline())
                if vcds_info:
                    log.debug("Found VCDS File with Driver Ver: {} HEX_V2: {}".format(vcds_info['driver_version'],vcds_info['hex_v2']))
                    obd_specs = {
                        'device' : 'VCDS',
                        'drv_ver' : vcds_info['driver_version'],
                        'fw_ver' : vcds_info['hex_v2']
                    }
                    return obd_specs
                
    def __determine_encoding(self, path):
        with open(path, 'rb') as f:
            blob = f.readline()
            encoding = chardet.detect(blob)['encoding']
            return encoding

    def __read_vcds_txt(self, path, enc):
        obd_specs = self.__get_obd_specs(path, enc)
        if not obd_specs:
            raise Exception("conversion error: invalid vcds file")
        with open(path,'r',encoding=enc) as f:
            result = {}
            dtc_data = []
            found_vam = False
            for line in f:
                if not found_vam:
                    vam = VIN_AND_MILAGE.match(line)
                    if vam:
                        result['vehicle'] = {'vin' : vam['vin']}
                        result['case'] = {'milage' : int(vam['milage'])}
                        found_vam = True
                obd_code = OBD_ERROR.match(line)
                if obd_code:
                    dtc_data.append(obd_code['error_code'])
            result['obd_data'] = {
                'dtc_data' : dtc_data,
                'obd_specs' : obd_specs
            }
            return result
    
