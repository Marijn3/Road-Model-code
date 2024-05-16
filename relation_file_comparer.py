msi_rel_file = "msi_relations.txt"
mtm_rel_file = "msi_relations_mtm.txt"

roadnrs = set()
msi_rels = dict()
found_log = list()
not_found_log = list()
lines_found = list()

with open(msi_rel_file, "r") as file:
    orig_lines = file.readlines()
    for index, line in enumerate(orig_lines):
        msi_1, relation, msi_2 = line.strip().split(" ")
        roadnr1, km1, lanenr1 = msi_1.split(":")
        roadnr2, km2, lanenr2 = msi_2.split(":")
        roadnrs.add(roadnr1)
        roadnrs.add(roadnr2)
        msi_rels[index] = {"roadnr1": roadnr1, "km1": km1, "lanenr1": lanenr1,
                           "rel": relation,
                           "roadnr2": roadnr2, "km2": km2, "lanenr2": lanenr2}

n_msi_rels = len(orig_lines)

with open(mtm_rel_file, "r") as file:
    orig_mtm_lines = file.readlines()
    for line in orig_mtm_lines:
        if line.startswith(tuple(roadnrs)):
            found_linking_msi = False
            msi_1, relation, msi_2 = line.strip().split(" ")
            roadnr1, km1, lanenr1 = msi_1.split(":")
            roadnr2, km2, lanenr2 = msi_2.split(":")
            for index, msi_rel in msi_rels.items():
                eq1 = roadnr1 == msi_rel["roadnr1"]
                eq2 = roadnr2 == msi_rel["roadnr2"]
                eq3 = lanenr2 == msi_rel["lanenr1"]
                eq4 = lanenr2 == msi_rel["lanenr2"]
                eq5 = abs(float(km1) - float(msi_rel["km1"])) <= 0.02
                eq6 = abs(float(km2) - float(msi_rel["km2"])) <= 0.02

                if all([eq1, eq2, eq3, eq4, eq5, eq6]):
                    found_log.append(f"{msi_1} {relation} {msi_2} links with {orig_lines[index].strip()}")
                    lines_found.append(index)
                    found_linking_msi = True
            if not found_linking_msi:
                not_found_log.append(f"{line.strip()} does not link with road model relations")

lines_found.sort(reverse=True)
print(lines_found)

for i in lines_found:
    orig_lines.pop(i)

if len(orig_lines) == 0:
    print("yay!")

print([f"{line.strip()} does not link with any MTM relations" for line in orig_lines])
print(found_log)
print(not_found_log)

with open("relation_comparison_log.txt", "w") as outfile:
    outfile.write(f"Relation comparison log between {msi_rel_file} and {mtm_rel_file}.\n")
    outfile.write(f"Found matches: {len(found_log)}\n")
    outfile.write(f"Relations from road model without match: {len(orig_lines)}/{n_msi_rels}\n")
    outfile.write(f"Relations from CGGTOP without match: {len(not_found_log)}/{len(orig_mtm_lines)}\n")
    outfile.write(f"\nROAD MODEL:\n")
    for line in orig_lines:
        outfile.write(f"{line.strip()} does not link with any MTM relations\n")






