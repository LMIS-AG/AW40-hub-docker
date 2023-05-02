from api.upload_filereader.formats.vcds_txt import VCDSTXTReader


class TestVCDSTXTReader:

    def test_read_file(self, vcds_txt_file):
        reader = VCDSTXTReader()
        result = reader.read_file(vcds_txt_file)
        assert isinstance(result, list)
        assert len(result) == 1

        # confirm expected obd data
        obd_data = result[0]["obd_data"]
        assert obd_data["dtcs"] == ["P1570", "C102D", "B10CD", "B1479"]
        assert obd_data["obd_specs"]["device"] == "VCDS"

        # confirm expected vehicle related information
        vehicle = result[0]["vehicle"]
        assert vehicle["vin"] == "TMBJB7NE4G0000000"

        # comfirm expected case related information
        case = result[0]["case"]
        assert case["milage"] == 55835
