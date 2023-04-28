from api.upload_filereader.formats.picoscope_csv import PicoscopeCSVReader
from numbers import Number


class TestPicoscopeCSVReader:

    def test_read_file(self, picoscope_csv_file):
        reader = PicoscopeCSVReader()
        result = reader.read_file(picoscope_csv_file)
        assert isinstance(result, list)
        assert len(result) == 1
        data = result[0]
        assert isinstance(data["sampling_rate"], Number)
        assert isinstance(data["duration"], Number)
        assert isinstance(data["signal"], list)
        assert data["device_specs"]["channel"] == "A"
        assert data["device_specs"]["type"] == "picoscope"
