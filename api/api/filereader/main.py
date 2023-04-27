import sys
import logging as log
from filereader_factory import filereader_factory

argv = sys.argv
user_file_format = None
if len(argv) <= 1:
    log.error("Missing File Argument")
    exit()
path = argv[1]
if len(argv) > 2:
    user_file_format = argv[2]
factory = filereader_factory()
if user_file_format:
    file_format = user_file_format
else:
    file_format = factory.guess_format(path)
    log.info("Guessing: {}".format(file_format))
if file_format:
    reader = factory.get_reader(file_format)
    if reader:
        try:
            result= reader.read_file(path)
            # TODO: Component is Channel name. 
            # Has to be replaced with real component identifier
            print(result)
        except Exception as e:
            log.error(e)
    else:
        log.error("No reader for given file found!")