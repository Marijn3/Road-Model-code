from road_model import DataFrameLader, WegModel
from msi_relations import MSINetwerk
from visualiser import SvgMaker
from ilp_input_creator import make_ILP_input, generate_file
from safety_areas import Rand, Aanvraag, AFZETTINGEN
from utils import *
logger = logging.getLogger(__name__)

ILP_ROADMODEL_FOLDER = "Server/Data/RoadModel"
MSI_RELATIONS_FILE = "msi_relations_roadmodel.txt"

start_time = time.time()

# Laad WEGGEG-bestanden in voor een gedefinieerd gebied, of voer coordinaten in.
dfl = DataFrameLader(locatie, "locaties.csv", data_folder)

import_time = time.time()

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

wegmodel_time = time.time()

# Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel
MSIs = MSINetwerk(wegmodel, maximale_zoekafstand=2000, kruisrelaties=False, bovenstroomse_secundaire_relaties=True)
MSIs.make_print(MSI_RELATIONS_FILE)  # (deze regel weglaten bij handmatig aanpassen bestand).

msi_network_time = time.time()

# Maak een visualisatie van het wegmodel en de afgeleide MSI-relaties.
SvgMaker(wegmodel, MSIs, MSI_RELATIONS_FILE, ILP_ROADMODEL_FOLDER, 1000, False)

visualization_time = time.time()

# Exporteer de MSI-eigenschappen naar een bestand.
ilp_input = make_ILP_input(MSIs, MSI_RELATIONS_FILE)
generate_file(ilp_input, ILP_ROADMODEL_FOLDER)

ilp_creation_time = time.time()

logger.info("")
logger.info(f"Data geïmporteerd in {import_time - start_time:.2f} seconden.")
logger.info(f"Wegmodel opgesteld in {wegmodel_time - import_time :.2f} seconden.")
logger.info(f"MSI netwerk opgesteld in {msi_network_time - wegmodel_time :.2f} seconden.")
logger.info(f"Afbeelding gemaakt in {visualization_time - msi_network_time :.2f} seconden.")
logger.info(f"ILP input gemaakt in {ilp_creation_time - visualization_time :.2f} seconden.")
logger.info(f"Totale tijd: {ilp_creation_time - start_time :.2f} seconden.")

# Instantieer een aanvraag (A27 Oosterhout)
if locatie == "A27Recht":
    # aanvraagAL = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.85,
    #                       km_end=14.40,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=False,
    #                       randen={"L": Rand(rijstrook=None, afstand=-2.0),
    #                               "R": Rand(rijstrook=None, afstand=-0.9)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagAR = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.93,
    #                       km_end=14.18,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=True,
    #                       randen={"L": Rand(rijstrook=None, afstand=1.2),
    #                               "R": Rand(rijstrook=None, afstand=3.0)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagBL = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.80,
    #                       km_end=14.03,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=True,
    #                       randen={"L": Rand(rijstrook=None, afstand=-1.0),
    #                               "R": Rand(rijstrook=None, afstand=-0.2)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagBR = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.80,
    #                       km_end=14.03,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=True,
    #                       randen={"L": Rand(rijstrook=None, afstand=0.2),
    #                               "R": Rand(rijstrook=None, afstand=1.0)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagCL = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.80,
    #                       km_end=14.03,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=False,
    #                       randen={"L": Rand(rijstrook=None, afstand=-1.0),
    #                               "R": Rand(rijstrook=None, afstand=-0.2)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagCR = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.80,
    #                       km_end=14.03,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=False,
    #                       randen={"L": Rand(rijstrook=None, afstand=0.2),
    #                               "R": Rand(rijstrook=None, afstand=1.0)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagDL = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.35,
    #                       km_end=13.42,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=True,
    #                       randen={"L": Rand(rijstrook=1, afstand=0.2),
    #                               "R": Rand(rijstrook=1, afstand=-0.9)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    # aanvraagDR = Aanvraag(wegmodel=wegmodel,
    #                       km_start=13.30,
    #                       km_end=13.40,
    #                       wegkant="R",
    #                       hectoletter="",
    #                       korter_dan_24h=True,
    #                       randen={"L": Rand(rijstrook=2, afstand=0.9),
    #                               "R": Rand(rijstrook=2, afstand=-0.3)},
    #                       afzetting=AFZETTINGEN.BAKENS,
    #                       )
    aanvraagDR = Aanvraag(wegmodel=wegmodel,
                          km=[16.1, 16.6],
                          wegkant="R",
                          hectoletter="",
                          korter_dan_24h=True,
                          randen={"L": Rand(rijstrook=2, afstand=0.9),
                                  "R": Rand(rijstrook=2, afstand=-0.3)},
                          afzetting=AFZETTINGEN.BAKENS,
                          )
