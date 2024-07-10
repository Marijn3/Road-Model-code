from road_model import DataFrameLader, WegModel
from msi_network import MSINetwerk
from run_profiles import Run
from utils import *
import traceback
logger = logging.getLogger(__name__)

run = Run(msi_relaties_overschrijven=True)

profiles = [run.vught, run.oosterhout, run.goirle, run.vinkeveen, run.a27, run.zonzeel, run.bavel,
            run.grijsoord, run.zuidasdok, run.everdingen, run.a2vk, run.lankhorst, run.amstel]

n_gelukt = 0

for profile in profiles:
    try:
        logger.info(f"{profile.name} verwerken...")
        dfl = DataFrameLader(profile)
        wegmodel = WegModel(dfl)
        MSIs = MSINetwerk(wegmodel)
    except Exception:
        logger.error(f"Error bij het verwerken van {profile.name}: {traceback.format_exc()}")
    else:
        n_gelukt += 1
        logger.info(f"{profile.name} verwerkt.")
logger.info(f"In totaal {n_gelukt} van de {len(profiles)} locaties verwerkt.")
