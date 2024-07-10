from road_model import DataFrameLader, WegModel
from msi_network import MSINetwerk
from utils import *
import traceback
logger = logging.getLogger(__name__)

locaties = ["Vught", "Oosterhout", "Goirle", "Vinkeveen", "A27",
            "Zonzeel", "Bavel", "Grijsoord", "Zuidasdok", "Everdingen", "A2VK", "Lankhorst", "Amstel"]

n_gelukt = 0

for locatie in locaties:
    try:
        logger.info(f"{locatie} verwerken...")
        dfl = DataFrameLader(locatie, "locaties.csv", "WEGGEG")
        wegmodel = WegModel(dfl)
        MSIs = MSINetwerk(wegmodel, maximale_zoekafstand=2000, kruisrelaties=True)
    except Exception:
        logger.error(f"Error bij het verwerken van {locatie}: {traceback.format_exc()}")
    else:
        n_gelukt += 1
        logger.info(f"{locatie} verwerkt.")
logger.info(f"In totaal {n_gelukt} van de {len(locaties)} locaties verwerkt.")
