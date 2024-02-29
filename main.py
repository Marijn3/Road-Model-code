from ilp_input_creator import *

# Laad alle bestanden en bewaar de GeoDataFrames in een class.
dfl = DataFrameLader("Vught")

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

# Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
MSIs = MSINetwerk(wegmodel)

# Exporteer de MSI-eigenschappen naar een bestand.
ilp_input = make_ILP_input(MSIs)
generate_file(ilp_input, "Server/Data/WEGGEG/WEGGEG.json")

# Instantieer een aanvraag
aanvraag = Aanvraag(wegmodel,
                    km_start=119.65,
                    km_end=119.7,
                    roadside="R",
                    # ruimte_links=1.5,
                    # ruimte_midden=[],
                    ruimte_rechts=1.5,
                    )

