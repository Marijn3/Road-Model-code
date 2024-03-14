from ilp_input_creator import *

# Laad alle bestanden voor een vooropgesteld gebied en bewaar de GeoDataFrames in een class.
# Gedefinieerde locaties: [Volledig correcte import] Vught, A27
#                         [Kleine verwerkingsfouten] A2Vink, Goirle, Zonzeel
#                         [Importfouten] A2VK
dfl = DataFrameLader("A27")

# Alternatief: voer eigen coördinaten in.
# dfl = DataFrameLader({"noord": 411600, "oost": 153000, "zuid": 407500, "west": 148300})

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

# # Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
# MSIs = MSINetwerk(wegmodel)
#
# # Exporteer de MSI-eigenschappen naar een bestand.
# ilp_input = make_ILP_input(MSIs)
# generate_file(ilp_input, "Server/Data/WEGGEG/WEGGEG.json")

# Instantieer een aanvraag
aanvraag = Aanvraag(wegmodel,
                    km_start=13.95,
                    km_end=13.98,
                    wegkant="R",
                    duur_korter_24h=True,
                    ruimte_links=2,
                    # ruimte_midden=[1],
                    # ruimte_rechts=1.5,
                    )
