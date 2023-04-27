import formats.formats as formats

class filereader_factory:
    def get_reader(self, format):
        try:
            reader = formats.SUPPORTED_FORMAT[format]()
        except:
            print("Format: {} is not supported".format(format))
            return None
        return reader
    
    def guess_format(self, path):
        for key in formats.SUPPORTED_FORMAT.keys():
            reader = formats.SUPPORTED_FORMAT[key]()
            if reader.probe(path):
                return key
        return None