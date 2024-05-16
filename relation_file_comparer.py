msi_rel_file = "msi_relations.txt"
mtm_rel_file = "msi_relations_mtm.txt"

roadnumbers_in_roadmodel_dataset = set()
roadmodel_msi_relations = dict()
found_relations_log = list()
roadmodel_line_numbers_found = list()
mtm_line_numbers_found = list()

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
# Load MTM-based MSI relations
# --------------------------------------------

with open(mtm_rel_file, "r") as file:
    original_mtm_lines = file.readlines()
    for mtm_index, line in enumerate(original_mtm_lines):
        # if line.startswith(tuple(roadnumbers_in_roadmodel_dataset)):
        if any(roadnumber in line for roadnumber in tuple(roadnumbers_in_roadmodel_dataset)):
            msi1, relation, msi2 = line.strip().split(" ")
            roadnumber1, km1, lanenumber1 = msi1.split(":")
            roadnumber2, km2, lanenumber2 = msi2.split(":")
            for roadmodel_index, roadmodel_msi_relation in roadmodel_msi_relations.items():
                km1_difference = round(abs(float(km1) - float(roadmodel_msi_relation["km1"])), 3)
                km2_difference = round(abs(float(km2) - float(roadmodel_msi_relation["km2"])), 3)

                eq1 = roadnumber1 == roadmodel_msi_relation["roadnumber1"]
                eq2 = roadnumber2 == roadmodel_msi_relation["roadnumber2"]
                eq3 = lanenumber2 == roadmodel_msi_relation["lanenumber1"]
                eq4 = lanenumber2 == roadmodel_msi_relation["lanenumber2"]
                eq5 = km1_difference <= 0.035
                eq6 = km2_difference <= 0.035

                if all([eq1, eq2, eq3, eq4, eq5, eq6]):
                    found_relations_log.append(
                        f"{msi1} {relation} {msi2}  <->  {original_roadmodel_lines[roadmodel_index].strip()}  "
                        f"(difference: {int(km1_difference * 1000)}m and {int(km2_difference * 1000)}m)"
                    )
                    roadmodel_line_numbers_found.append(roadmodel_index)
                    mtm_line_numbers_found.append(mtm_index)
                    break

# --------------------------------------------
# Process data
# --------------------------------------------

roadmodel_line_numbers_found.sort(reverse=True)
roadmodel_lines = original_roadmodel_lines.copy()
for i in roadmodel_line_numbers_found:
    roadmodel_lines.pop(i)

mtm_line_numbers_found.sort(reverse=True)
mtm_lines = original_mtm_lines.copy()
for i in mtm_line_numbers_found:
    mtm_lines.pop(i)

mtm_lines_filtered = list()
for line in mtm_lines:
    if any(roadnr in line for roadnr in tuple(roadnumbers_in_roadmodel_dataset)):
        mtm_lines_filtered.append(line)

if len(roadmodel_lines) == 0:
    print("All relations from road model matched. See log file for more details.")
else:
    print("Not all relations from road model matched. See log file for more details.")

# --------------------------------------------
# Write comparison output log
# --------------------------------------------

with open("relation_comparison_log.txt", "w") as outfile:
    outfile.write(f"Relation comparison log between {msi_rel_file} and {mtm_rel_file}.\n\n")
    outfile.write(f"Found matches: {len(found_relations_log)}\n")
    outfile.write(f"Relations from road model without match: {len(roadmodel_lines)}/{len(original_roadmodel_lines)}\n")
    outfile.write(f"Relations from CGGTOP without match: {len(mtm_lines)}/{len(original_mtm_lines)}\n")
    outfile.write(f"\nFOUND MATCHES:\n")
    for line in found_relations_log:
        outfile.write(f"{line}\n")

    outfile.write(f"\nROAD MODEL UNMATCHED LINES:\n")
    if not roadmodel_lines:
        outfile.write(f"-\n")
    for line in roadmodel_lines:
        outfile.write(f"{line.strip()}\n")

    outfile.write(f"\nMTM UNMATCHED LINES (FILTERED BY ROAD NUMBER):\n")
    if not mtm_lines_filtered:
        outfile.write(f"-\n")
    for line in mtm_lines_filtered:
        outfile.write(f"{line.strip()}\n")
