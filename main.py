# =====================================
# Script bij afstudeerproject "Derivation and analysis of lane signaling".
# Geschreven door Marijn Minkenberg, 2024, TU/e MSc kandidaat.
#
# Dit is het hoofdbestand. Stel hieronder uw voorkeuren in.
# Profielen kunen worden toegevoegd en aangepast in Settings/profiles.py.
# Invoer: WEGGEG-data.
# Uitvoer: MSI-relatiebestand, SVG-visualisatie, JSON-invoerbestand voor ILP.
# =====================================

from Settings.profiles import *
from application_steps import run_application

# Maak aanpassingen in onderstaande regels:
run_application(
    profiel=Vught(),  # Profiel en locatie om uit te voeren.
    msi_relaties_overschrijven=True,  # Keuze om (aangepaste) MSI relaties te behouden of overschrijven.
    logger_instelling="INFO"  # Keuze uit DEBUG, INFO of WARNING.
)
