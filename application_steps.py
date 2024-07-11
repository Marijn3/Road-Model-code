from Road_model.road_model import DataFrameLader, WegModel
from MSI_network.msi_network import MSINetwerk
from Visualisation.visualiser import SvgMaker
from ILP.ilp_input_creator import make_ILP_input, generate_file
from Safety_areas.safety_areas import Aanvraag
from Settings.profiles import Profile
from Settings.area_requests import aanvragen
import logging
import time


def init_logger(level: str = "DEBUG") -> logging.Logger:
    logger = logging.getLogger(__name__)

    if level == "DEBUG":
        logging_level = logging.DEBUG
    elif level == "INFO":
        logging_level = logging.INFO
    elif level == "WARNING":
        logging_level = logging.WARNING
    else:
        logging_level = logging.DEBUG

    # Initialize the logger
    logging.basicConfig(filename="data_processing.log",
                        filemode="w",
                        level=logging_level,
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


def run_application(profiel: Profile, msi_relaties_overschrijven: bool = True, logger_instelling: str = "INFO") -> None:
    logger = init_logger(level=logger_instelling)

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
