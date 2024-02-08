from functions import *

# Laad alle bestanden en bewaar de GeoDataFrames in een class
dfl = DataFrameLader("Vught")

# Stel een wegmodel op met de ingeladen GeoDataFrames
wegmodel = WegModel(dfl)

# Inspecteren voor DEMO (Vught)
wegmodel.print_props(121.6, 'L')  # Twee secties
wegmodel.print_props(121.8, 'L')  # Eén sectie
wegmodel.print_props(110.9, 'L')  # Geen secties
wegmodel.print_props(121.4, 'R')  # Andere kant van de weg, met een rijstrookbeëindiging.

MSIs = MSINetwerk(wegmodel)
