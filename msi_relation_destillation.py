
CGGTOP_FOLDER = "Input_data/ZUIDNEDERLAND.00295"  # This file is not publicized.
MSI_RELATIONS_OUTPUT = "msi_relations_cggtop.txt"

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


def get_msis_from_line(msi_line: str) -> tuple[str, str]:
    msi_line = msi_line.strip().replace("/", "")

    if "=" in msi_line:
        msi_line = msi_line.split("=")[1]

    msi_nr_part = msi_line[0]
    msi_name_part = msi_line[2:]

    msi_name_part = msi_name_part.replace(",", ".")
    return msi_nr_part, msi_name_part


with open(CGGTOP_FOLDER, "r") as cggtop_file:
    row_name = ""
    relation_type = None
    for original_line in cggtop_file.readlines():
        line = original_line.strip()

        # Catch section start by specific header line.
        if not line == "!SECTION DESCRIPTION CLOSED" and line.startswith("!SECTION DESCRIPTION "):
            # Determine the roadnumber for this section.
            roadnumber = line.replace("!SECTION DESCRIPTION ", "").strip()
            continue

        # Catch onderstation start by indentation.
        if original_line[0:2] == " !":
            km_text = line.split(sep=" ")[0][1:]
            km = float(km_text.replace(",", "."))
            row_name = f"{roadnumber}:{km:.3f}"
            continue

        if line.startswith("!DETSTN=") or line.startswith("!VLUCHTSTROOK"):
            # We're done with this onderstation. No more relations are given in the file after this line.
            row_name = None

        if row_name:
            if original_line.startswith("   !"):
                relation_type = determine_relation_type(line)
            if relation_type:
                msi_nr, other_msi_name = get_msis_from_line(line)
                msi_network.append(f"{row_name}:{msi_nr} {relation_type} {other_msi_name}")

with open(MSI_RELATIONS_OUTPUT, "w") as outfile:
    for entry in msi_network:
        outfile.write(f"{entry}\n")
