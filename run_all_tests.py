from Road_model.road_model import DataFrameLader, WegModel
from MSI_network.msi_network import MSINetwerk
from Settings.profiles import *
from application_steps import init_logger
import traceback

logger = init_logger(level="INFO")
profiles = [Vught(), Oosterhout(), Goirle(), Vinkeveen(), A27(), A27Recht(), Zonzeel(), Bavel(),
            Grijsoord(), Zuidasdok(), Everdingen(), A2VK(), Lankhorst(), Amstel()]
n_gelukt = 0

for profile in profiles:
    try:
        logger.info(f"{profile.name} verwerken...")
        dataframe_lader = DataFrameLader(profile)
        wegmodel = WegModel(dataframe_lader)
        msi_netwerk = MSINetwerk(wegmodel)
    except Exception:
        logger.error(f"Error bij het verwerken van {profile.name}: {traceback.format_exc()}")
    else:
        n_gelukt += 1
        logger.info(f"{profile.name} verwerkt.")
logger.info(f"In totaal {n_gelukt} van de {len(profiles)} locaties verwerkt.")
