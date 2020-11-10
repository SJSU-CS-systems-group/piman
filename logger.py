import logging
import logging.config
import os
# create the logger before doing imports since everyone is going
# to use them
local_logfile = './logging.conf'
if os.path.isfile(local_logfile):
    logging.config.fileConfig(local_logfile)
else:
    zipfile = os.path.dirname(__file__)
    with ZipFile(zipfile) as z:
        fd = z.open("logging.conf", mode='r')
        # convert to a string
        confstr = fd.read().decode()
        logging.config.fileConfig(io.StringIO(confstr))

#create logger using configuration
logger = logging.getLogger('pimanlogger')
