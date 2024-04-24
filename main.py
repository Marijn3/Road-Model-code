from road_model import DataFrameLader, WegModel
from msi_relations import MSINetwerk
from visualiser import SvgMaker
from ilp_input_creator import make_ILP_input, generate_file
from safety import *

ILP_ROADMODEL_FOLDER = "Server/Data/RoadModel"
MSI_RELATIONS_FILE = "msi_relations.txt"

# ========= Gedefinieerde locaties =========
# Volledig correcte import : Vught, Oosterhout, Goirle, Vinkeveen, A27
# Verwerkingsfouten : [MultiLineString] Zonzeel
#                     [Tapers] Bavel
#                     [MSI relations] Grijsoord*, Zuidasdok*, Everdingen*
# Importfouten : A2VK, Lankhorst
# * = Na het oplossen van registratiefouten

# Laad WEGGEG-bestanden in voor een gedefinieerd gebied, of voer coordinaten in.
dfl = DataFrameLader("Oosterhout", "data/locaties.csv")
# dfl = DataFrameLader({"noord": 433158.9132, "oost": 100468.8980, "zuid": 430753.1611, "west": 96885.3299},
#                      "data/locaties.csv")

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

# Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
MSIs = MSINetwerk(wegmodel, maximale_zoekafstand=2000, alle_secundaire_relaties=True)
MSIs.make_print(MSI_RELATIONS_FILE)

# Maak een visualisatie van het wegmodel en de afgeleide MSI-relaties.
SvgMaker(wegmodel, MSI_RELATIONS_FILE, f"{ILP_ROADMODEL_FOLDER}/RoadModelVisualisation.svg", 1000, False)

# Exporteer de MSI-eigenschappen naar een bestand.
ilp_input = make_ILP_input(MSIs, MSI_RELATIONS_FILE)
generate_file(ilp_input, f"{ILP_ROADMODEL_FOLDER}/LSC.json")

# Instantieer een aanvraag (A27 Oosterhout)
aanvraag = Aanvraag(wegmodel,
                    km_start=13.95,
                    km_end=13.98,
                    wegkant="R",
                    korter_dan_24h=True,
                    ruimte_links=1,
                    stroken=[1],
                    ruimte_rechts=6,
                    afzetting=AFZETTING_BAKENS,
                    )
