from road_model import DataFrameLader, WegModel
from msi_network import MSINetwerk
from visualiser import SvgMaker
from ilp_input_creator import make_ILP_input, generate_file
from safety_areas import Rand, Aanvraag, AFZETTINGEN
from utils import *
from run_profiles import Run
logger = logging.getLogger(__name__)

run = Run(msi_relaties_overschrijven=True)
profile = run.grijsoord

print(f"Proces voor {profile.name} gestart...")
start_time = time.time()

# Laad WEGGEG-bestanden in voor een gedefinieerd gebied, of voer coordinaten in.
dfl = DataFrameLader(location=profile.location, weggeg_data_folder=profile.data_folder)
import_time = time.time()

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)
wegmodel_time = time.time()

# Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
MSIs = MSINetwerk(wegmodel,
                  maximale_zoekafstand=profile.maximum_row_search_distance,
                  kruisrelaties=profile.cross_relations)

if profile.overwrite_msi_relations:
    MSIs.make_print(profile.msi_relations_file)
msi_network_time = time.time()

# Maak een visualisatie van het wegmodel en de afgeleide MSI-relaties.
SvgMaker(wegmodel, MSIs, profile.msi_relations_file,
         profile.ilp_roadmodel_folder, profile.image_size, profile.msis_on_road)
visualization_time = time.time()

# Exporteer de MSI-eigenschappen naar een bestand.
ilp_input = make_ILP_input(MSIs, profile.msi_relations_file)
generate_file(ilp_input, profile.ilp_roadmodel_folder)
ilp_creation_time = time.time()

logger.info(f"\n==============================================\n"
            f"Data import gedaan in {import_time - start_time:.2f} seconden.\n"
            f"Wegmodel opgesteld in {wegmodel_time - import_time:.2f} seconden.\n"
            f"MSI netwerk opgesteld in {msi_network_time - wegmodel_time:.2f} seconden.\n"
            f"Afbeelding gemaakt in {visualization_time - msi_network_time:.2f} seconden.\n"
            f"ILP input gemaakt in {ilp_creation_time - visualization_time:.2f} seconden.\n"
            f"Totale tijd: {ilp_creation_time - start_time:.2f} seconden.\n"
            f"==============================================")

print(f"Proces succesvol afgerond in {ilp_creation_time - start_time:.2f} seconden. "
      f"Zie voor meer informatie het log-bestand.")

# Instantieer een aanvraag (A27 Oosterhout)
if locatie == "A27Recht":
    aanvraagAL = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=None, afstand=-1.8),
                                  "R": Rand(rijstrook=None, afstand=-1.2)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagAR = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=None, afstand=1.2),
                                  "R": Rand(rijstrook=None, afstand=1.8)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagBL = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=None, afstand=-1.0),
                                  "R": Rand(rijstrook=None, afstand=-0.2)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagBR = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=None, afstand=0.2),
                                  "R": Rand(rijstrook=None, afstand=1.0)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagCL = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=False,
                          randen={"L": Rand(rijstrook=None, afstand=-1.0),
                                  "R": Rand(rijstrook=None, afstand=-0.22)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagCR = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=False,
                          randen={"L": Rand(rijstrook=None, afstand=0.22),
                                  "R": Rand(rijstrook=None, afstand=1.0)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagDL = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=1, afstand=0.3),
                                  "R": Rand(rijstrook=1, afstand=-1.1)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagDR = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=2, afstand=1.1),
                                  "R": Rand(rijstrook=2, afstand=-0.3)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
    aanvraagBarriers = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=False,
                          randen={"L": Rand(rijstrook=None, afstand=-1.8),
                                  "R": Rand(rijstrook=None, afstand=-0.4)},
                          afzetting=AFZETTINGEN.BARRIER_BOVEN_80CM,
                          )
