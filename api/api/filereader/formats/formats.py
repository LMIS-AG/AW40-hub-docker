import formats.picoscope_mat
import formats.picoscope_csv
import formats.vcds_txt
import formats.omniscope_v1

SUPPORTED_FORMAT = {
    "Picoscope CSV": formats.picoscope_csv.picoscope_csv_reader,
    "Picoscope MAT": formats.picoscope_mat.picoscope_mat_reader,
    "VCDS TXT": formats.vcds_txt.vcds_txt_reader,
    "Omniscope V1 RAW": formats.omniscope_v1.omniscope_v1_reader
}