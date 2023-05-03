from api.upload_filereader.formats.picoscope_mat import PicoscopeMATReader
from numbers import Number
import pytest


class TestPicoscopeMATReader:

    @pytest.mark.parametrize(
        "file,expected_channels",
        [
            ("picoscope_1ch_mat_file", ["A"]),
            ("picoscope_4ch_mat_file", ["A", "B", "C", "D"])
        ])
    def test_read_file(self, file, expected_channels, request):
        # use request fixture to convert file parameter from str to actual
        # value of picoscope file fixture
        file = request.getfixturevalue(file)

        # convert file
        reader = PicoscopeMATReader()
        result = reader.read_file(file)

        # assert expectations
        assert isinstance(result, list)
        assert len(result) == len(expected_channels)
        for i, data in enumerate(result):
            assert isinstance(data["sampling_rate"], Number)
            assert isinstance(data["duration"], Number)
            assert isinstance(data["signal"], list)
            assert data["device_specs"]["channel"] == expected_channels[i]
            assert data["device_specs"]["type"] == "picoscope"
