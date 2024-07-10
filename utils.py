from copy import deepcopy
import math
import time
import logging

# Initialize the logger
logging.basicConfig(filename="data_processing_log.txt",
                    filemode="w",
                    level=logging.DEBUG,
                    # format='[%(asctime)s] (%(levelname)s) %(name)s -> %(funcName)s: %(message)s'
                    format='[%(asctime)s] (%(levelname)s): %(message)s')

# Set a higher level for external libraries such as fiona to filter out their debug messages
external_logger = logging.getLogger('fiona')
external_logger.setLevel(logging.INFO)
external_logger2 = logging.getLogger('matplotlib')
external_logger2.setLevel(logging.INFO)
external_logger3 = logging.getLogger('urllib3')
external_logger3.setLevel(logging.INFO)

DISTANCE_TOLERANCE = 0.1  # [m] Tolerantie-afstand voor overlap tussen punt- en lijngeometrieën.
