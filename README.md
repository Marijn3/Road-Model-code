# Road Model Derivation from WEGGEG Data
The code provided in this repository allows the user to derive a road model from WEGGEG data.
This road model is used to derive MSI (Matrix Signal Indicator) relations and properties.
The road model and MSI relations together are used to generate a visualisation.
The MSI relations and properties are used to generate an input file
for the ILP (Integer Linear Programming) formulation provided previously by Jeroen van Meurs. 
This ILP formulation is used to simulate the MSI network. A GUROBI installation and license is required.

# Application structure
## main.py
This file should be run. The profile of choice can be set here.

## Settings/profiles.py
This file contains the various pre-programmed user profiles.
Profiles in the `Run` class can be adjusted or added manually.

## application_steps.py
This file executes all functions from the other files in the appropriate order.
It logs the results in `relation_comparison.log`.

## Road_model/road_model.py
Defines classes and functions to load WEGGEG data and store it as dataframes,
on which basic manipulations can be performed. The `WegModel` class constructs
the road model from the dataframes and stores it.

## MSI_network/msi_network.py
Defines classes and functions to derive MSI relations based on the road model.
These are stored in the `MSINetwork` class. This class can output the MSI network
relations to a separate file in `MSI_relation_comparison/msi_relations_roadmodel.txt`.

## MSI_relation_comparison/mtm_msi_relation_destillation.py
Contains functions to distill MSI relations from an MTM file (not included).
The derived relations are stored in `MSI_relation_comparison/msi_relations_mtm.txt`.

## MSI_relation_comparison/relation_file_comparer.py
Contains functions to compare two relation files, one from MTM and one from
the road model. It logs the results in `relation_comparison.log`.

## Visualisation/visualiser.py
Defines `SvgMaker` class that uses an established road model and MSI relations
to generate an svg file. This svg can be updated based on requested legends.

## ILP/ilp_input_creator.py
Defines functions to convert a combination of the `MSINetwork` class and an
MSI network file to input for the ILP formulation.

## Safety_areas/safety_areas.py
Defines classes and functions to enable processing of a workspace request. Workspace requests
are set in `Settings/area_requests.py`.
When the ILP process is active, it performs a legend request based on the workspace request.
Plots are generated of the safety areas. For now, this code makes some assumptions that are
valid only in the _A27Recht_ profile.

# Code decisions
* Naming conventions and terminology from WEGGEG itself are adhered to. See WEGGEG documentation 
[here](https://downloads.rijkswaterstaatdata.nl/weggeg/geogegevens/shapefile/Documentatie/Handleiding%20Weggeg/).
* Documentation of the main file and the profiles file is in Dutch, as this should be accessible for DEMO purposes.
Logs are in Dutch. Other files, containing the majority of the code, are mostly English.

# Known issues
* Wedge (Puntstuk) registrations on the left side of the road are not accounted for in determining the lane bounds.
This causes missing primary relations in some cases.
* Left emergency lane does not always properly affect the lane shift value.
* The determination of whether a property starts or ends on a section does not 
take into account the shift value between the sections.