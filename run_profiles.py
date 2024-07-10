class Profile:
    def __init__(
            self,
            locatie: str | dict,
            precisie: float = 0.00001,
            secundaire_kruisrelaties: bool = False,
            maximale_afstand: int = 2000,
            msi_relaties_overschrijven: bool = False,
            afbeeldingsformaat: int = 1000,
            msis_boven_weg: bool = False,
            data_folder: str = "WEGGEG",
            ilp_wegmodel_folder: str = "Server/Data/RoadModel",
            msi_relatie_uitvoerbestand: str = "msi_relations_roadmodel.txt",
            ) -> None:
        """
        Maakt een run-profiel aan met alle instellingen om de hoofdapplicatie te draaien.
        Args:
            locatie (str or dict): Locatie om te verwerken. Indien een string, wordt een passend gebied gezocht.
            precisie (float): Precisie bij geometrieberekeningen. 0.00001 is standaardwaarde voor bijna alle locaties.
            secundaire_kruisrelaties (bool): Keuze om secundaire kruisrelaties toe te passen.
            maximale_afstand (int): Meters afstand (schatting)
            msi_relaties_overschrijven (bool): Keuze om (aangepaste) MSI relaties te behouden of overschrijven.
            afbeeldingsformaat (int): Pixels breedte van afbeelding.
            msis_boven_weg (bool): Keuze voor tekenmodus op de weg of langs de weg.
            data_folder (str): Folder waar WEGGEG brondata in geplaatst is.
            ilp_wegmodel_folder (str): Pad naar locatie waar waar svg en JSON uitvoer geplaatst worden (voor ILP)
            msi_relatie_uitvoerbestand (str): Pad naar MSI-relatie uitvoerbestand.
        """
        self.name = locatie if isinstance(locatie, str) else "custom"
        self.location = locatie_coords.get(locatie) if isinstance(locatie, str) else locatie
        self.image_size = afbeeldingsformaat
        self.data_folder = data_folder
        self.precision = precisie
        self.cross_relations = secundaire_kruisrelaties
        self.msis_on_road = msis_boven_weg
        self.maximum_row_search_distance = maximale_afstand
        self.ilp_roadmodel_folder = ilp_wegmodel_folder
        self.msi_relations_file = msi_relatie_uitvoerbestand
        self.overwrite_msi_relations = msi_relaties_overschrijven


# ========= Gedefinieerde locaties =========
# Correcte import : Vught, Oosterhout, Goirle, Vinkeveen, A27, Bavel, A27Recht, A2VK*
# Verwerkingsfouten in MSI-relaties : Grijsoord*, Zuidasdok*, Everdingen*, Lankhorst, Amstel*, Zonzeel
# * = Na het oplossen van registratiefouten


class Run:
    def __init__(self, msi_relaties_overschrijven: bool = True):

        self.vught = Profile(
            locatie="Vught",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.bavel = Profile(
            locatie="Bavel",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.a2vk = Profile(
            locatie="A2VK",
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.oosterhout = Profile(
            locatie="Oosterhout",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.vinkeveen = Profile(
            locatie="Vinkeveen",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.zonzeel = Profile(
            locatie="Zonzeel",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.goirle = Profile(
            locatie="Goirle",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.zuidasdok = Profile(
            locatie="Zuidasdok",
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.everdingen = Profile(
            locatie="Everdingen",
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.a27 = Profile(
            locatie="A27",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.grijsoord = Profile(
            locatie="Grijsoord",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.lankhorst = Profile(
            locatie="Lankhorst",
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.amstel = Profile(
            locatie="Amstel",
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.amstel_casestudy = Profile(
            locatie="Amstel",
            data_folder="WEGGEG-Zuidasdok",  # Folder met case study data.
            precisie=0.0001,  # [m] Aangepast op grid van case study data.
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.a27recht = Profile(
            locatie="A27Recht",
            secundaire_kruisrelaties=True,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )

        self.custom = Profile(
            locatie={"west": 112962, "zuid": 371521, "oost": 181731, "noord": 418831},
            secundaire_kruisrelaties=False,
            msi_relaties_overschrijven=msi_relaties_overschrijven
        )


locatie_coords = {
    "Vught": {"noord": 411600, "oost": 153000, "zuid": 407500, "west": 148300},
    "A2VK": {"noord": 349300, "oost": 190650, "zuid": 331350, "west": 182500},
    "Oosterhout": {"noord": 407500, "oost": 120800, "zuid": 405700, "west": 119300},
    "Vinkeveen": {"noord": 472500, "oost": 129600, "zuid": 469700, "west": 125300},
    "Zonzeel": {"noord": 407700, "oost": 109300, "zuid": 405400, "west": 105200},
    "Goirle": {"noord": 395500, "oost": 133000, "zuid": 393600, "west": 128000},
    "Bavel": {"noord": 397500, "oost": 119000, "zuid": 395000, "west": 115000},
    "Zuidasdok": {"noord": 484000, "oost": 120200, "zuid": 483000, "west": 117000},
    "Everdingen": {"noord": 444100, "oost": 136900, "zuid": 442500, "west": 134200},
    "A27": {"noord": 408800, "oost": 122000, "zuid": 402100, "west": 116000},
    "Grijsoord": {"noord": 449000, "oost": 185900, "zuid": 447700, "west": 183600},
    "Lankhorst": {"noord": 520800, "oost": 210800, "zuid": 519100, "west": 209300},
    "Amstel": {"noord": 484200, "oost": 126100, "zuid": 480900, "west": 118300},
    "A27Recht": {"noord": 410600, "oost": 121000, "zuid": 407000, "west": 119000},
}

