from copy import deepcopy
import math
import logging

# ========= Gedefinieerde locaties =========
# Volledig correcte import : Vught, Oosterhout, Goirle, Vinkeveen, A27
# Verwerkingsfouten : [MultiLineString] Zonzeel
#                     [MSI relaties] Bavel, Grijsoord*, Zuidasdok*, Everdingen*, A2VK*, Lankhorst, Amstel*
# * = Na het oplossen van registratiefouten

case_study = True

if case_study:
    locatie = "Amstel"
    data_folder = "WEGGEG-Zuidasdok"
    CALCULATION_PRECISION = 0.0001  # [m] Aangepast op grid van case study data.
else:
    locatie = "Vught"
    data_folder = "WEGGEG"
    CALCULATION_PRECISION = 0.00001  # [m] Precisie van coordinaten van lijngeometrieën.

# Initialize the logger
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] (%(levelname)s) %(name)s -> %(funcName)s: %(message)s')

# Set a higher level for external libraries such as fiona to filter out their debug messages
external_logger = logging.getLogger('fiona')
external_logger.setLevel(logging.INFO)
external_logger2 = logging.getLogger('matplotlib')
external_logger2.setLevel(logging.INFO)

DISTANCE_TOLERANCE = 0.1  # [m] Tolerantie-afstand voor overlap tussen punt- en lijngeometrieën.
