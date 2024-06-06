from copy import deepcopy
import math
import logging

# Initialize the logger
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] (%(levelname)s) %(name)s -> %(funcName)s: %(message)s')

# Set a higher level for external libraries such as fiona to filter out their debug messages
external_logger = logging.getLogger('fiona')
external_logger.setLevel(logging.INFO)

DISTANCE_TOLERANCE = 0.3  # [m] Tolerantie-afstand voor overlap tussen punt- en lijngeometrieën.
CALCULATION_PRECISION = 0.0001  # [m] Precisie van coordinaten van lijngeometriën.
