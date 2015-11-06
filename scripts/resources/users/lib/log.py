import logging


filehandler = False

level = logging.DEBUG
#level = logging.INFO

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(level)

formatter = logging.Formatter('%(asctime)s - %(levelname)s\t- %(module)s::%(funcName)s - %(message)s')
#logger.setFormatter(formatter)

if filehandler:
	fh = logging.FileHandler('adsync.log')
	fh.setLevel(level)
	fh.setFormatter(formatter)
	logger.addHandler(fh)
else:
	ch = logging.StreamHandler()
	ch.setLevel(level)
	ch.setFormatter(formatter)
	logger.addHandler(ch)
