# Road Model Derivation from WEGGEG Data
The code provided in this repository allows the user to derive a road model from WEGGEG data.
This road model can be used to derive MSI (Matrix Signal Indicator) relations and properties.
The road model and MSI relations together can be used to generate a visualisation.
The MSI relations and properties can be used to generate an input file
for the ILP (Integer Linear Programming) formulation by TU/e. This can 'complete' legend requests.
The code for this is available here: (Link to follow). (A GUROBI installation is required.)
In future work, it will be possible to define a workspace request, which will
be converted to a legend request and then be completed using the ILP formulation.

# File structure
## main.py
The intended usage and order of the files can be found in main.py.
This file imports all functions from the other files and calls them
in order. The desired location for which to run the code can be specified here.

## road_model.py
Defines classes and functions to load WEGGEG data and store it as dataframes,
on which basic manipulations can be performed. The class 'WegModel' constructs
the road model from the dataframes and stores it.

## msi_relations.py
Defines classes and functions to derive MSI relations based on the road model.
These are stored in the 'MSINetwork' class.

## visualiser.py
Defines visualiser class that uses an established road model and MSI network
to generate an SVG. This SVG can be updated based on the requested legends, but
this requires a refresh. WIP to update this in realtime.

## ilp_input_creator.py
Defines functions to convert an 'MSINetwork' class to input for the ILP formulation.

## safety.py
(WIP) Defines classes and functions to enable processing of a workspace request.

# DEMO
The main.py file provides five examples where the import works well, such that
a demo can be performed. You might need to adjust some output paths before running the code.

# Code decisions
* Naming conventions and terminology from WEGGEG itself are adhered to. See WEGGEG documentation:
https://downloads.rijkswaterstaatdata.nl/weggeg/geogegevens/shapefile/Documentatie/Handleiding%20Weggeg/
* The main file contains Dutch code, as this should be accessible for DEMO purposes,
but the other files are mostly English.
* The DYN-V property of an MSI (row) allows a maximum speed in case of open rush hour lanes,
or time-related decreases in maximum speed, to be set. These properties are available in the
data and thus processed into the road model, but they are not assigned to DYN-V in the
MSINetwork. This is because the ILP formulation uses the DYN-V as a way to dynamically
request any speed, and thus the DYN-V property should not be filled in by default.