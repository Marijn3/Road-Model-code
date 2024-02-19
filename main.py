from ilp_input_creator import *

# Laad alle bestanden en bewaar de GeoDataFrames in een class.
dfl = DataFrameLader("Vught")

# Stel een wegmodel op met de ingeladen GeoDataFrames.
wegmodel = WegModel(dfl)

# # Bepaal MSI relaties en eigenschappen gebaseerd op het wegmodel.
# MSIs = MSINetwerk(wegmodel)
#
# # Exporteer de MSI-eigenschappen naar een bestand.
# ilp_input = make_ILP_input(MSIs)
# generate_file(ilp_input, "output_data.json")