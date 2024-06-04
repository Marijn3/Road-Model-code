from road_model import DataFrameLader, WegModel
from msi_relations import MSINetwerk
from visualiser import SvgMaker
from ilp_input_creator import make_ILP_input, generate_file
from safety_areas import Rand, Aanvraag, AFZETTINGEN

ILP_ROADMODEL_FOLDER = "Server/Data/RoadModel"
MSI_RELATIONS_FILE = "msi_relations_roadmodel.txt"

locatie = "Amstel"

# ========= Gedefinieerde locaties =========
# Volledig correcte import : Vught, Oosterhout, Goirle, Vinkeveen, A27
# Verwerkingsfouten : [MultiLineString] Zonzeel
#                     [MSI relaties] Bavel, Grijsoord*, Zuidasdok*, Everdingen*, A2VK*, Lankhorst, Amstel
# * = Na het oplossen van registratiefouten

# Laad WEGGEG-bestanden in voor een gedefinieerd gebied, of voer coordinaten in.
dfl = DataFrameLader(locatie, "locaties.csv", "WEGGEG-Zuidasdok")

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

# Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel
MSIs = MSINetwerk(wegmodel, maximale_zoekafstand=2000, alle_secundaire_relaties=True)
MSIs.make_print(MSI_RELATIONS_FILE)  # (deze regel weglaten bij handmatig aanpassen bestand).

# Maak een visualisatie van het wegmodel en de afgeleide MSI-relaties.
SvgMaker(wegmodel, MSIs, MSI_RELATIONS_FILE, ILP_ROADMODEL_FOLDER, 1000, False)

# Exporteer de MSI-eigenschappen naar een bestand.
ilp_input = make_ILP_input(MSIs, MSI_RELATIONS_FILE)
generate_file(ilp_input, ILP_ROADMODEL_FOLDER)

# Instantieer een aanvraag (A27 Oosterhout)
if locatie == "Oosterhout":
    aanvraag1 = Aanvraag(wegmodel=wegmodel,
                         km_start=13.95,
                         km_end=13.98,
                         wegkant="R",
                         hectoletter="",
                         korter_dan_24h=True,
                         randen={"L": Rand(rijstrook=None, afstand=1.2),
                                 "R": Rand(rijstrook=None, afstand=3.5)},
                         afzetting=AFZETTINGEN.BAKENS,
                         )
    aanvraag2 = Aanvraag(wegmodel=wegmodel,
                         km_start=13.95,
                         km_end=13.98,
                         wegkant="R",
                         hectoletter="",
                         korter_dan_24h=True,
                         randen={"L": Rand(rijstrook=2, afstand=0.9),
                                 "R": Rand(rijstrook=2, afstand=-0.3)},
                         afzetting=AFZETTINGEN.BAKENS,
                         )
