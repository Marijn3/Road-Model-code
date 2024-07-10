msi_rel_file = "msi_relations_roadmodel.txt"
cggtop_rel_file = "msi_relations_cggtop.txt"

ALLOWED_KM_DIFFERENCE = 0.080

roadmodel_dataset_extent = dict()
found_relations_log = list()

roadmodel_msi_relations = dict()
cggtop_msi_relations = dict()

roadmodel_line_numbers_found = list()
cggtop_line_numbers_found = list()

# --------------------------------------------
# Load road model relations
# --------------------------------------------

with open(msi_rel_file, "r") as file:
    original_roadmodel_lines = file.readlines()
    for roadmodel_index, line in enumerate(original_roadmodel_lines):
        msi1, relation, msi2 = line.strip().split(" ")
        roadnumber1, km1, lanenumber1 = msi1.split(":")
        roadnumber2, km2, lanenumber2 = msi2.split(":")

        # determine km windows by min and max value encountered
        if roadnumber1 not in roadmodel_dataset_extent.keys():
            roadmodel_dataset_extent[roadnumber1] = (km1, km1)  # Min and max so far
        else:
            km_min, km_max = roadmodel_dataset_extent.get(roadnumber1)
            new_km_min = float(km_min) if float(km_min) <= float(km1) else float(km1)
            new_km_max = float(km_max) if float(km_max) >= float(km1) else float(km1)
            roadmodel_dataset_extent[roadnumber1] = (new_km_min, new_km_max)

        if roadnumber2 not in roadmodel_dataset_extent.keys():
            roadmodel_dataset_extent[roadnumber2] = (km2, km2)  # Min and max so far
        else:
            km_min, km_max = roadmodel_dataset_extent.get(roadnumber2)
            new_km_min = float(km_min) if float(km_min) <= float(km2) else float(km2)
            new_km_max = float(km_max) if float(km_max) >= float(km2) else float(km2)
            roadmodel_dataset_extent[roadnumber2] = (new_km_min, new_km_max)

        roadmodel_msi_relations[roadmodel_index] = {"roadnumber1": roadnumber1, "km1": km1, "lanenumber1": lanenumber1,
                                                    "rel": relation,
                                                    "roadnumber2": roadnumber2, "km2": km2, "lanenumber2": lanenumber2}

# --------------------------------------------
# Load CGGTOP-based MSI relations
# --------------------------------------------

with open(cggtop_rel_file, "r") as file:
    original_cggtop_lines = file.readlines()
    for cggtop_index, line in enumerate(original_cggtop_lines):
        # if line.startswith(tuple(roadnumbers_in_roadmodel_dataset)):
        if any(roadnumber in line for roadnumber in roadmodel_dataset_extent.keys()):
            msi1, relation, msi2 = line.strip().split(" ")
            roadnumber1, km1, lanenumber1 = msi1.split(":")
            roadnumber2, km2, lanenumber2 = msi2.split(":")
            km_min1, km_max1 = roadmodel_dataset_extent.get(roadnumber1, (0.0, 0.0))
            km_min2, km_max2 = roadmodel_dataset_extent.get(roadnumber2, (0.0, 0.0))
            if (km_min1 - ALLOWED_KM_DIFFERENCE <= float(km1) <= km_max1 + ALLOWED_KM_DIFFERENCE
                    and km_min2 - ALLOWED_KM_DIFFERENCE <= float(km2) <= km_max2 + ALLOWED_KM_DIFFERENCE):
                cggtop_msi_relations[cggtop_index] = {
                    "roadnumber1": roadnumber1, "km1": km1, "lanenumber1": lanenumber1,
                    "rel": relation,
                    "roadnumber2": roadnumber2, "km2": km2, "lanenumber2": lanenumber2
                }

# --------------------------------------------
# Process data
# --------------------------------------------

for cggtop_index, cggtop_msi_relation in cggtop_msi_relations.items():
    for roadmodel_index, roadmodel_msi_relation in roadmodel_msi_relations.items():
        eq1 = cggtop_msi_relation["roadnumber1"] == roadmodel_msi_relation["roadnumber1"]
        eq2 = cggtop_msi_relation["roadnumber2"] == roadmodel_msi_relation["roadnumber2"]

        if not (eq1 or eq2):
            continue

        eq3 = cggtop_msi_relation["lanenumber1"] == roadmodel_msi_relation["lanenumber1"]
        eq4 = cggtop_msi_relation["lanenumber2"] == roadmodel_msi_relation["lanenumber2"]

        if not (eq3 or eq4):
            continue

        km1_difference = round(abs(float(cggtop_msi_relation["km1"]) - float(roadmodel_msi_relation["km1"])), 3)
        km2_difference = round(abs(float(cggtop_msi_relation["km2"]) - float(roadmodel_msi_relation["km2"])), 3)

        eq5 = km1_difference <= ALLOWED_KM_DIFFERENCE
        eq6 = km2_difference <= ALLOWED_KM_DIFFERENCE

        if all([eq1, eq2, eq3, eq4, eq5, eq6]):
            found_relations_log.append(f"{original_cggtop_lines[cggtop_index].strip()}   \t<->    "
                                       f"{original_roadmodel_lines[roadmodel_index].strip()}    \t(difference: "
                                       f"{int(km1_difference * 1000)}m and {int(km2_difference * 1000)}m)")
            roadmodel_line_numbers_found.append(roadmodel_index)
            cggtop_line_numbers_found.append(cggtop_index)
            break

roadmodel_line_numbers_found.sort(reverse=True)
roadmodel_lines = original_roadmodel_lines.copy()
for i in roadmodel_line_numbers_found:
    roadmodel_lines.pop(i)

cggtop_line_numbers_found.sort(reverse=True)
cggtop_lines = original_cggtop_lines.copy()
for i in cggtop_line_numbers_found:
    cggtop_lines.pop(i)

cggtop_lines_filtered = list()
for line in cggtop_lines:
    if any(roadnr in line for roadnr in roadmodel_dataset_extent.keys()):
        msi1, relation, msi2 = line.strip().split(" ")
        roadnumber1, km1, lanenumber1 = msi1.split(":")
        roadnumber2, km2, lanenumber2 = msi2.split(":")
        km_min1, km_max1 = roadmodel_dataset_extent.get(roadnumber1, (0.0, 0.0))
        km_min2, km_max2 = roadmodel_dataset_extent.get(roadnumber2, (0.0, 0.0))
        if (km_min1 - ALLOWED_KM_DIFFERENCE <= float(km1) <= km_max1 + ALLOWED_KM_DIFFERENCE
                and km_min2 - ALLOWED_KM_DIFFERENCE <= float(km2) <= km_max2 + ALLOWED_KM_DIFFERENCE):
            cggtop_lines_filtered.append(line)

if len(roadmodel_lines) == 0:
    print("All relations from road model matched. See log file for more details.")
else:
    print("Not all relations from road model matched. See log file for more details.")

# --------------------------------------------
# Write comparison output log
# --------------------------------------------

with open("relation_comparison.log", "w") as outfile:
    outfile.write(f"This is an automatically generated relation comparison log between files {msi_rel_file}\n"
                  f"and {cggtop_rel_file}, obtained by running relation_file_comparer.py.\n\n")
    outfile.write(f"Roads in road model dataset: {roadmodel_dataset_extent}\n\n")
    outfile.write(f"Found matches: {int(len(found_relations_log)/2)}\n")
    outfile.write(f"Relations from road model without match: "
                  f"{int(len(roadmodel_lines)/2)}/{int(len(original_roadmodel_lines)/2)}\n")
    outfile.write(f"Relations from CGGTOP without match: "
                  f"{int(len(cggtop_lines_filtered)/2)}/{int(len(cggtop_msi_relations)/2)} "
                  f"(filtered by road numbers and km)\n")

    outfile.write(f"\nROAD MODEL UNMATCHED RELATIONS:\n")
    if not roadmodel_lines:
        outfile.write(f"-\n")
    for line in roadmodel_lines:
        outfile.write(f"{line.strip()}\n")

    outfile.write(f"\nCGGTOP UNMATCHED RELATIONS (MSIS FILTERED BY ROAD NUMBER AND KM RANGE):\n")
    if not cggtop_lines_filtered:
        outfile.write(f"-\n")
    for line in cggtop_lines_filtered:
        outfile.write(f"{line.strip()}\n")

    outfile.write(f"\nALL MATCHED RELATIONS:\n")
    outfile.write(f"[Road model MSI relation]\t\t\t\t   [CGGTOP MSI relation]\n")
    for line in found_relations_log:
        outfile.write(f"{line}\n")
