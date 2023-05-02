from api.upload_filereader.formats.omniscope_v1 import OmniscopeV1Reader


class TestPicoscopeCSVReader:

    def test_read_file(self, omniscope_v1_file):
        reader = OmniscopeV1Reader()
        result = reader.read_file(omniscope_v1_file)
        assert isinstance(result, list)
        assert len(result) == 1
        data = result[0]
        assert isinstance(data["signal"], list)
        assert data["device_specs"]["type"] == "omniscope v1"
