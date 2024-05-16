msi_rel_file = "msi_relations_roadmodel.txt"
cggtop_rel_file = "msi_relations_cggtop.txt"

roadnumbers_in_roadmodel_dataset = set()
roadmodel_msi_relations = dict()
cggtop_msi_relations = dict()

found_relations_log = list()
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
        roadnumbers_in_roadmodel_dataset.add(roadnumber1)
        roadnumbers_in_roadmodel_dataset.add(roadnumber2)
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
        if any(roadnumber in line for roadnumber in tuple(roadnumbers_in_roadmodel_dataset)):
            msi1, relation, msi2 = line.strip().split(" ")
            roadnumber1, km1, lanenumber1 = msi1.split(":")
            roadnumber2, km2, lanenumber2 = msi2.split(":")
            cggtop_msi_relations[cggtop_index] = {"roadnumber1": roadnumber1, "km1": km1, "lanenumber1": lanenumber1,
                                                  "rel": relation,
                                                  "roadnumber2": roadnumber2, "km2": km2, "lanenumber2": lanenumber2}

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

        eq5 = km1_difference <= 0.035
        eq6 = km2_difference <= 0.035

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

original_cggtop_lines_filtered = list()
for line in original_cggtop_lines:
    if any(roadnr in line for roadnr in tuple(roadnumbers_in_roadmodel_dataset)):
        original_cggtop_lines_filtered.append(line)

cggtop_lines_filtered = list()
for line in cggtop_lines:
    if any(roadnr in line for roadnr in tuple(roadnumbers_in_roadmodel_dataset)):
        cggtop_lines_filtered.append(line)

if len(roadmodel_lines) == 0:
    print("All relations from road model matched. See log file for more details.")
else:
    print("Not all relations from road model matched. See log file for more details.")

# --------------------------------------------
# Write comparison output log
# --------------------------------------------

with open("relation_comparison_log.txt", "w") as outfile:
    outfile.write(f"This is an automatically generated relation comparison log between files {msi_rel_file}\n"
                  f"and {cggtop_rel_file}, obtained by running relation_file_comparer.py.\n\n")
    outfile.write(f"Road numbers in road model dataset: {roadnumbers_in_roadmodel_dataset}\n")
    outfile.write(f"Found matches: {len(found_relations_log)}\n")
    outfile.write(f"Relations from road model without match: {len(roadmodel_lines)}/{len(original_roadmodel_lines)}\n")
    outfile.write(f"Relations from CGGTOP without match: "
                  f"{len(cggtop_lines_filtered)}/{len(original_cggtop_lines_filtered)} (filtered by road numbers)\n")

    outfile.write(f"\nROAD MODEL UNMATCHED LINES:\n")
    if not roadmodel_lines:
        outfile.write(f"-\n")
    for line in roadmodel_lines:
        outfile.write(f"{line.strip()}\n")

    outfile.write(f"\nALL MATCHED LINES:\n")
    outfile.write(f"[Road model MSI relation]\t\t\t\t   [CGGTOP MSI relation]\n")
    for line in found_relations_log:
        outfile.write(f"{line}\n")

    outfile.write(f"\nCGGTOP UNMATCHED LINES (FILTERED BY ROAD NUMBER):\n")
    if not cggtop_lines_filtered:
        outfile.write(f"-\n")
    for line in cggtop_lines_filtered:
        outfile.write(f"{line.strip()}\n")
