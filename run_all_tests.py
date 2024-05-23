from road_model import DataFrameLader, WegModel
from msi_relations import MSINetwerk
from utils import *
import traceback
logger = logging.getLogger(__name__)

locaties = ["Vught", "Oosterhout", "Goirle", "Vinkeveen", "A27",
            "Zonzeel", "Bavel", "Grijsoord", "Zuidasdok", "Everdingen", "A2VK", "Lankhorst"]

for locatie in locaties:
    try:
        dfl = DataFrameLader(locatie, "data/locaties.csv")
        wegmodel = WegModel(dfl)
        MSIs = MSINetwerk(wegmodel, maximale_zoekafstand=2000, alle_secundaire_relaties=True)
    except Exception:
        logger.error(f"Error processing location {locatie}: {traceback.format_exc()}")
    else:
        logger.info(f"Finished processing {locatie}.")
