from .omniscope_v1 import OmniscopeV1Reader
from .picoscope_csv import PicoscopeCSVReader
from .picoscope_mat import PicoscopeMATReader
from .vcds_txt import VCDSTXTReader

SUPPORTED_FORMATS = {
    "Picoscope CSV": PicoscopeCSVReader,
    "Picoscope MAT": PicoscopeMATReader,
    "Omniscope V1 RAW": OmniscopeV1Reader,
    "VCDS TXT": VCDSTXTReader
}
