from copy import deepcopy
import math
import logging

# Initialize the logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] (%(levelname)s) %(name)s -> %(funcName)s: %(message)s')

# Set a higher level for external libraries such as fiona to filter out their debug messages
external_logger = logging.getLogger('fiona')
external_logger.setLevel(logging.INFO)

