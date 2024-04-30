CGGTOP_FOLDER = "data/ZUIDNEDERLAND.00295"
MSI_RELATIONS_OUTPUT = "msi_relations_mtm.txt"

with open(CGGTOP_FOLDER, "r") as cggtop_file:
    for line in cggtop_file.readlines():
        if line.rstrip() == "!SECTION DESCRIPTION CLOSED":
            print("End this section")
        elif line[0:20] == "!SECTION DESCRIPTION":
            roadnumber = line.strip("!SECTION DESCRIPTION ").rstrip()
            print(f"Start this section: {roadnumber}")

        if line[0:2] == " !":
            # New onderstation
            print(line.strip())
            onderstation_data = line.strip().split(sep=" ")
            km_text = onderstation_data[0][1:]
            km = float(km_text.replace(",", "."))
            # roadnumber = onderstation_data[3]
            print(f"{roadnumber}:{km:.3f}")


