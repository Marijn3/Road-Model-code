msi_rel_file = "msi_relations.txt"
mtm_rel_file = "msi_relations_mtm.txt"

roadnumbers_in_roadmodel_dataset = set()
roadmodel_msi_relations = dict()
found_relations_log = list()
not_found_relations_log = list()
line_numbers_found = list()

# --------------------------------------------
# Load road model relations
# --------------------------------------------

with open(msi_rel_file, "r") as file:
    original_roadmodel_lines = file.readlines()
    for index, line in enumerate(original_roadmodel_lines):
        msi1, relation, msi2 = line.strip().split(" ")
        roadnumber1, km1, lanenumber1 = msi1.split(":")
        roadnumber2, km2, lanenumber2 = msi2.split(":")
        roadnumbers_in_roadmodel_dataset.add(roadnumber1)
        roadnumbers_in_roadmodel_dataset.add(roadnumber2)
        roadmodel_msi_relations[index] = {"roadnr1": roadnumber1, "km1": km1, "lanenr1": lanenumber1,
                                          "rel": relation,
                                          "roadnr2": roadnumber2, "km2": km2, "lanenr2": lanenumber2}

# --------------------------------------------
# Load MTM-based MSI relations
# --------------------------------------------

with open(mtm_rel_file, "r") as file:
    orig_mtm_lines = file.readlines()
    for line in orig_mtm_lines:
        found_linking_msi = False
        # if line.startswith(tuple(roadnumbers_in_roadmodel_dataset)):
        if any(roadnumber in line for roadnumber in tuple(roadnumbers_in_roadmodel_dataset)):
            msi1, relation, msi2 = line.strip().split(" ")
            roadnumber1, km1, lanenumber1 = msi1.split(":")
            roadnumber2, km2, lanenumber2 = msi2.split(":")
            for index, msi_rel in roadmodel_msi_relations.items():
                km1_difference = round(abs(float(km1) - float(msi_rel["km1"])), 3)
                km2_difference = round(abs(float(km2) - float(msi_rel["km2"])), 3)

                eq1 = roadnumber1 == msi_rel["roadnr1"]
                eq2 = roadnumber2 == msi_rel["roadnr2"]
                eq3 = lanenumber2 == msi_rel["lanenr1"]
                eq4 = lanenumber2 == msi_rel["lanenr2"]
                eq5 = km1_difference <= 0.035
                eq6 = km2_difference <= 0.035

                if all([eq1, eq2, eq3, eq4, eq5, eq6]):
                    found_relations_log.append(
                        f"{msi1} {relation} {msi2}  <->  {original_roadmodel_lines[index].strip()}  "
                        f"(difference: {int(km1_difference * 1000)}m and {int(km2_difference * 1000)}m)"
                    )
                    line_numbers_found.append(index)
                    found_linking_msi = True
                    break
        if not found_linking_msi:
            not_found_relations_log.append(line)

# --------------------------------------------
# Process data
# --------------------------------------------

line_numbers_found.sort(reverse=True)

roadmodel_lines = original_roadmodel_lines.copy()

for i in line_numbers_found:
    roadmodel_lines.pop(i)

if len(roadmodel_lines) == 0:
    print("All relations matched. See log file for more details.")
else:
    print("Not all relations matched. See log file for more details.")

# --------------------------------------------
# Write comparison output log
# --------------------------------------------

with open("relation_comparison_log.txt", "w") as outfile:
    outfile.write(f"Relation comparison log between {msi_rel_file} and {mtm_rel_file}.\n\n")
    outfile.write(f"Found matches: {len(found_relations_log)}\n")
    outfile.write(f"Relations from road model without match: {len(roadmodel_lines)}/{len(original_roadmodel_lines)}\n")
    outfile.write(f"Relations from CGGTOP without match: {len(not_found_relations_log)}/{len(orig_mtm_lines)}\n")
    outfile.write(f"\nFOUND MATCHES:\n")
    for line in found_relations_log:
        outfile.write(f"{line}\n")

    outfile.write(f"\nROAD MODEL UNMATCHED LINES:\n")
    if not roadmodel_lines:
        outfile.write(f"-\n")
    for line in roadmodel_lines:
        outfile.write(f"{line.strip()}\n")

    outfile.write(f"\nMTM UNMATCHED LINES (FILTERED BY ROAD NUMBER):\n")
    if not not_found_relations_log:
        outfile.write(f"-\n")
    for line in not_found_relations_log:
        if any(roadnr in line for roadnr in tuple(roadnumbers_in_roadmodel_dataset)):
            outfile.write(f"{line.strip()}\n")
