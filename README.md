The code provided in this repository allows the user to derive a road model from WEGGEG data.
This road model can be used to derive MSI relations and properties.
The road model and MSI relations can be used to generate a visualisation.
The MSI relations and properties can be used to generate an input file for ILP.
The ILP formulation allows legend requests to be 'solved'. The code for this is available here: (Link to follow)
In future work, it will be possible to do some workspace requests.

# File structure

## main.py
Main file to be executed. This imports all functions from the other files and
calls them in order. The desired location for which to run the code can be specified here.

## road_model.py
Defines classes and functions to load WEGGEG data and store it as dataframes,
on which basic manipulations can be performed. The class 'WegModel' constructs
the road model from the dataframes.

## msi_relations.py


## visualiser.py


## ilp_input_creator


## safety.py



# Code decisions
A couple of things are excluded from the code, since they are not used
in the established context of this project. They are described below.
* 
* 
(Houd ook bij wat je anders zou doen (als je het niet op JvM specifiek zou moeten aansluiten))



