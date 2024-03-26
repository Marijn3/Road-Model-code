from ilp_input_creator import *

# Laad alle bestanden voor een gegeven gebied en bewaar de GeoDataFrames in een class.

# ========= Gedefinieerde locaties =========
# Volledig correcte import : Vught, Oosterhout, Goirle, Vinkeveen, A27
# Verwerkingsfouten : [MultiLineString] Zonzeel
#                     [MSI relations] Zuidasdok, Bavel, Everdingen
# Importfouten : A2VK

dfl = DataFrameLader("Vught")

# Alternatief: voer eigen coördinaten in.
# dfl = DataFrameLader({"noord": 433158.9132, "oost": 100468.8980, "zuid": 430753.1611, "west": 96885.3299})

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

# Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
MSIs = MSINetwerk(wegmodel, maximale_zoekafstand=2600, alle_secundaire_relaties=True)

# Maak een visualisatie van het wegmodel en de afgeleide MSI-relaties.
SvgMaker(dfl, wegmodel, MSIs, "Server/Data/WEGGEG/road_visualization.svg", 1000, False)

# # Exporteer de MSI-eigenschappen naar een bestand.
ilp_input = make_ILP_input(MSIs)
generate_file(ilp_input, "Server/Data/WEGGEG/WEGGEG.json")

# # Instantieer een aanvraag (A27 Oosterhout)
# aanvraag = Aanvraag(wegmodel,
#                     km_start=13.95,
#                     km_end=13.98,
#                     wegkant="R",
#                     duur_korter_24h=True,
#                     # ruimte_links=1,
#                     ruimte_midden=[1],
#                     # ruimte_rechts=1.5,
#                     )
