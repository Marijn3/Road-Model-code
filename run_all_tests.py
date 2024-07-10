from Road_Model.road_model import DataFrameLader, WegModel
from MSI_network.msi_network import MSINetwerk
from Settings.run_profiles import Run
from application_steps import init_logger
import traceback

logger = init_logger(level="INFO")
run = Run()
profiles = [run.vught, run.oosterhout, run.goirle, run.vinkeveen, run.a27, run.zonzeel, run.bavel,
            run.grijsoord, run.zuidasdok, run.everdingen, run.a2vk, run.lankhorst, run.amstel]
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
