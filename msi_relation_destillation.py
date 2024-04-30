from copy import deepcopy

CGGTOP_FOLDER = "data/ZUIDNEDERLAND.00295"
MSI_RELATIONS_OUTPUT = "msi_relations_mtm.txt"

msi_network = []


def determine_relation_type(relation_line: str) -> str | None:
    if relation_line.startswith("!PRIMARY-UP="):
        return "u"
    elif relation_line.startswith("!PRIMARY-DOWN="):
        return "d"
    elif relation_line.startswith("!SECONDARY-UP="):
        return "us"
    elif relation_line.startswith("!SECONDARY-DOWN="):
        return "ds"
    elif relation_line.startswith("!BROADEN-UP="):
        return "ub"
    elif relation_line.startswith("!BROADEN-DOWN="):
        return "db"
    elif relation_line.startswith("!NARROW-UP="):
        return "un"
    elif relation_line.startswith("!NARROW-DOWN="):
        return "dn"
    elif relation_line.startswith("!TAPER-DOWN="):
        return "dt"
    elif relation_line.startswith("!TAPER_UP="):
        return "dt"
    else:
        return None


with open(CGGTOP_FOLDER, "r") as cggtop_file:
    row_name = ""
    for original_line in cggtop_file.readlines():
        line = original_line.strip()

        if line == "!SECTION DESCRIPTION CLOSED":
            # Do things to finish this section
            # print("Ending this section.")

        elif line.startswith("!SECTION DESCRIPTION"):
            # Determine the roadnumber for this section
            roadnumber = line.strip("!SECTION DESCRIPTION ").rstrip()
            # print(f"Starting this section: {roadnumber}")

        if original_line[0:2] == " !":  # This indentation indicates a new onderstation
            km_text = line.split(sep=" ")[0][1:]
            km = float(km_text.replace(",", "."))
            # roadnumber = onderstation_data[3]
            row_name = f"{roadnumber}:{km:.3f}"
            print(f"This is row {row_name}")

        if line.startswith("!DETSTN=") or line.startswith("!VLUCHTSTROOK"):
            # We're done with this onderstation. No more relations are given in the file.
            row_name = None

        if row_name:
            relation_type = determine_relation_type(line)
            if relation_type:
                print(f"I have primary {relation_type} relations with:")

                msi_network.append(f"{row_name}:NR_HERE {relation_type} OTHER_MSI_HERE")



print(msi_network)
