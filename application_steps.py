from road_model import DataFrameLader, WegModel
from msi_network import MSINetwerk
from visualiser import SvgMaker
from ilp_input_creator import make_ILP_input, generate_file
from safety_areas import Rand, Aanvraag, AFZETTINGEN
from run_profiles import Profile
import logging
import time


def init_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)

    # Initialize the logger
    logging.basicConfig(filename="data_processing.log",
                        filemode="w",
                        level=logging.DEBUG,
                        format='[%(asctime)s] (%(levelname)s) %(name)s -> %(funcName)s: %(message)s')
    # Shorter format: '[%(asctime)s] (%(levelname)s): %(message)s'

    # Set a higher level for external libraries such as fiona to filter out their debug messages
    external_logger = logging.getLogger('fiona')
    external_logger.setLevel(logging.INFO)
    external_logger2 = logging.getLogger('matplotlib')
    external_logger2.setLevel(logging.INFO)
    external_logger3 = logging.getLogger('urllib3')
    external_logger3.setLevel(logging.INFO)
    return logger


def run_application(profiel: Profile, msi_relaties_overschrijven: bool = True) -> None:
    logger = init_logger()

    print(f"Verwerkingsproces voor {profiel.name} gestart...")
    start_time = time.time()

    # Laad WEGGEG-bestanden in voor een gedefinieerd gebied, of voer coordinaten in.
    dataframe_lader = DataFrameLader(profiel)
    import_time = time.time()

    # Stel een wegmodel op met de ingeladen GeoDataFrames.
    wegmodel = WegModel(dataframe_lader)
    wegmodel_time = time.time()

    # Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
    msi_netwerk = MSINetwerk(wegmodel)

    # Exporteer MSI relaties naar bestand, afhankelijk van instelling.
    if msi_relaties_overschrijven:
        msi_netwerk.make_print()
    msi_network_time = time.time()

    # Maak een visualisatie van het wegmodel en de afgeleide MSI-relaties.
    SvgMaker(wegmodel, msi_netwerk)
    visualization_time = time.time()

    # Exporteer de MSI-eigenschappen naar een bestand.
    ilp_input = make_ILP_input(msi_netwerk)
    generate_file(ilp_input, profiel.ilp_roadmodel_folder)
    ilp_creation_time = time.time()

    logger.info(f"\n==============================================\n"
                f"Data import gedaan in {import_time - start_time:.2f} seconden.\n"
                f"Wegmodel opgesteld in {wegmodel_time - import_time:.2f} seconden.\n"
                f"MSI netwerk opgesteld in {msi_network_time - wegmodel_time:.2f} seconden.\n"
                f"Afbeelding gemaakt in {visualization_time - msi_network_time:.2f} seconden.\n"
                f"ILP input gemaakt in {ilp_creation_time - visualization_time:.2f} seconden.\n"
                f"Totale tijd: {ilp_creation_time - start_time:.2f} seconden.\n"
                f"==============================================")

    print(f"Verwerkingsproces succesvol afgerond in {ilp_creation_time - start_time:.2f} seconden. "
          f"Zie voor meer informatie het log-bestand.")

    # Instantieer een aanvraag (A27 Oosterhout)
    if profiel.name == "A27Recht":
        for naam, instellingen in aanvragen.items():
            logger.info(f"Aanvraag {naam} wordt gedaan.")
            Aanvraag(wegmodel=wegmodel, instellingen=instellingen)


aanvragen = {
    "Categorie A links": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": True,
        "randen": {"L": Rand(rijstrook=None, afstand=-1.8), "R": Rand(rijstrook=None, afstand=-1.2)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie A rechts": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": True,
        "randen": {"L": Rand(rijstrook=None, afstand=1.2), "R": Rand(rijstrook=None, afstand=1.8)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie B links": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": True,
        "randen": {"L": Rand(rijstrook=None, afstand=-1.0), "R": Rand(rijstrook=None, afstand=-0.2)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie B rechts": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": True,
        "randen": {"L": Rand(rijstrook=None, afstand=0.2), 
                   "R": Rand(rijstrook=None, afstand=1.0)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie C links": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": False,
        "randen": {"L": Rand(rijstrook=None, afstand=-1.0), 
                   "R": Rand(rijstrook=None, afstand=-0.22)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie C rechts": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": False,
        "randen": {"L": Rand(rijstrook=None, afstand=0.22), 
                   "R": Rand(rijstrook=None, afstand=1.0)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie D links": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": True,
        "randen": {"L": Rand(rijstrook=1, afstand=0.3), 
                   "R": Rand(rijstrook=1, afstand=-1.1)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie D rechts": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": True,
        "randen": {"L": Rand(rijstrook=2, afstand=1.1), 
                   "R": Rand(rijstrook=2, afstand=-0.3)},
        "afzetting": AFZETTINGEN.BAKENS,
    },
    "Categorie A links met barriers": {
        "km": [16.1, 16.6],
        "wegkant": "R",
        "hectoletter": "",
        "korter_dan_24h": False,
        "randen": {"L": Rand(rijstrook=None, afstand=-1.8), 
                   "R": Rand(rijstrook=None, afstand=-0.4)},
        "afzetting": AFZETTINGEN.BARRIER_BOVEN_80CM,
    },
}
