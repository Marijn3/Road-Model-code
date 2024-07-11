# =====================================
# Code behorende aan afstudeerproject "Derivation and analysis of lane signaling".
# Geschreven door Marijn Minkenberg, 2024, MSc kandidaat aan TU/e.
#
# Dit is het hoofdbestand. Stel hieronder uw voorkeuren in.
# Profielen kunen worden toegevoegd en aangepast in run_profiles.py.
# Invoer: WEGGEG-data.
# Uitvoer: MSI-relatiebestand, SVG-visualisatie, JSON-invoerbestand voor ILP.
# =====================================

from Settings.profiles import Run
from application_steps import run_application

run = Run()

# Maak aanpassingen in onderstaande regels:
run_application(
    profiel=run.vught,  # Locatie om uit te voeren.
    msi_relaties_overschrijven=True,  # Keuze om (aangepaste) MSI relaties te behouden of overschrijven.
)
