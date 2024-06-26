import geopandas as gpd
import pandas as pd
import csv
from shapely import *
from utils import *
logger = logging.getLogger(__name__)


class PositieEigenschappen:
    """Positional properties for sections and points in the road model."""

    def __init__(self, rijrichting: str = "", wegnummer: str = "", hectoletter: str = "",
                 km: list = None, geometrie: Point | LineString = None):
        """
        Initialise positional properties class, filling it with provided properties
        Args:
            rijrichting (str): Driving direction ('L' or 'R') for BPS locating
            wegnummer (str): Road name for BPS locating
            hectoletter (str): Hecto character BPS locating
            km (list): Kilometer registrations at the start and end of the section,
                or in case of a point, the kilometer registration of the point.
            geometrie (Point or LineString): Shape geometry
        Example:
            pos = PositieEigenschappen("L", "A10", "", [50.1, 52.3], LineString(...))
        """
        self.rijrichting = rijrichting
        self.wegnummer = wegnummer
        self.hectoletter = hectoletter
        self.km = km if km is not None else float()
        self.geometrie = geometrie

    def __repr__(self):
        wegnr_repr = self.wegnummer if self.wegnummer else " "
        richting_repr = self.rijrichting if self.rijrichting else " "
        hecto_repr = self.hectoletter if self.hectoletter else " "
        km_repr = f"[{self.km[0]:<7.3f}, {self.km[1]:<7.3f}]" if isinstance(self.km, list) else f"{self.km:<7.3f}"
        return f"{wegnr_repr}{richting_repr} {hecto_repr} \t{km_repr} km \t"


class LijnVerwerkingsEigenschappen:
    """Processing properties for sections in the road model."""

    def __init__(self):
        self.vergentiepunt_start = None
        self.vergentiepunt_einde = None
        self.sectie_stroomopwaarts = None
        self.sectie_stroomafwaarts = None
        self.sectie_afbuigend_stroomopwaarts = None
        self.sectie_afbuigend_stroomafwaarts = None
        self.start_kenmerk = {}
        self.einde_kenmerk = {}
        self.aantal_stroken = None
        self.aantal_hoofdstroken = None
        self.aantal_rijstroken_links = None
        self.aantal_rijstroken_rechts = None
        self.heeft_verwerkingsfout = False


class PuntVerwerkingsEigenschappen:
    """Processing properties for points in the road model."""

    def __init__(self):
        self.sectie_ids = []
        self.ingaande_secties = []
        self.uitgaande_secties = []
        self.aantal_hoofdstroken = None
        self.aantal_stroken = None
        self.lokale_hoek = None


class ObjectInfo:
    """Properties for sections and points in the road model."""

    def __init__(self, pos_eigs: PositieEigenschappen = None, obj_eigs: dict = None, lijn: bool = True):
        self.pos_eigs = PositieEigenschappen() if pos_eigs is None else pos_eigs
        self.obj_eigs = {} if obj_eigs is None else obj_eigs
        self.verw_eigs = LijnVerwerkingsEigenschappen() if lijn else PuntVerwerkingsEigenschappen()

    def __repr__(self):
        typename = "Sectie" if isinstance(self.pos_eigs.km, list) else "Punt"
        return (f"{typename} op {self.pos_eigs} met eigenschappen: "
                f"{self.obj_eigs}")


class DataFrameLader:
    """
    A class for loading GeoDataFrames from shapefiles based on a specified location extent.

    Public attributes:
        data (dict): Dictionary to store GeoDataFrames for each layer.
        extent (box): The extent of the specified location.
    """

    __VERGENCE_NAME_MAPPING = {
        "U": "Uitvoeging",
        "D": "Splitsing",
        "C": "Samenvoeging",
        "I": "Invoeging"
    }

    def __init__(self, locatie: str | dict, locations_csv_pad: str, data_folder: str) -> None:
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            locatie (str or dict): The name of the location or a dict of coordinates,
                indicating the bounding box to the area to be loaded.
            locations_csv_pad (str): Path towards csv file defining locations by coordinates.
            data_folder (str): Path to WEGGEG data folder.
        Example:
            dfl = DataFrameLader("Everdingen")
            dfl = DataFrameLader({"noord": 433158.9132, "oost": 100468.8980, "zuid": 430753.1611, "west": 96885.3299})
        """
        # List all data layer files to be loaded. Same structure as WEGGEG.
        self.__FILE_PATHS = [
            f"{data_folder}/Wegvakken/wegvakken.dbf",
            f"{data_folder}/Rijstroken/rijstroken.dbf",
            f"{data_folder}/Mengstroken/mengstroken.dbf",
            f"{data_folder}/Kantstroken/kantstroken.dbf",
            f"{data_folder}/Maximum snelheid/max_snelheden.dbf",
            f"{data_folder}/Convergenties/convergenties.dbf",
            f"{data_folder}/Divergenties/divergenties.dbf",
            f"{data_folder}/Rijstrooksignaleringen/strksignaleringn.dbf",
        ]
        
        self.data = {}
        self.__locations_csv_path = locations_csv_pad
        self.__lane_mapping_h = self.__construct_lane_mapping("H")
        self.__lane_mapping_t = self.__construct_lane_mapping("T")

        if isinstance(locatie, str):
            coords = self.__get_coords_from_csv(locatie)
        elif isinstance(locatie, dict):
            coords = locatie
        else:
            raise NotImplementedError(f"Input of type {type(locatie)} is not supported. "
                                      f"Use a str or dict instead.")

        self.extent = box(xmin=coords["west"], ymin=coords["zuid"], xmax=coords["oost"], ymax=coords["noord"])
        self.__load_dataframes()

    @staticmethod
    def __construct_lane_mapping(direction: str) -> dict:
        """
        Constructs mapping from lane registration to (nLanes, Special feature)
        All registrations with T as kantcode are marked in the opposite direction.
        Args:
            direction (str): Either "H" or "T", for 'heen' and 'terug'.
        Returns:
            Lane mapping dictionary.
        """
        mapping = {}
        for i in range(1, 8):
            for j in range(1, 8):
                # Exclude entries where the difference is more than 1 (e.g. 1 -> 3)
                if abs(i - j) <= 1:
                    key = f"{i} -> {j}"
                    if direction == "H":
                        if i == j:
                            value = (i, None)
                        elif i > j:
                            value = (i, "StrookEinde")
                        else:
                            value = (j, "StrookStart")
                    else:  # For direction "T"
                        if i == j:
                            value = (i, None)
                        elif i > j:
                            value = (i, "StrookStart")
                        else:
                            value = (j, "StrookEinde")
                    mapping[key] = value
        # Special taper registrations, added outside the loop to improve readability.
        if direction == "H":
            mapping["1 -> 1.6"] = (1, None)  # "Taper opkomst start")
            mapping["1.6 -> 1"] = (1, None)  # "Taper afloop einde")
            mapping["2 -> 1.6"] = (2, "TaperConvergentie")  # wel 2 stroken breed, want 2 breed bij start
            mapping["1.6 -> 2"] = (1, "TaperDivergentie")  # eigenlijk 2 stroken breed, maar niet zo geregistreerd
        if direction == "T":
            mapping["1 -> 1.6"] = (1, None)  # "Taper afloop einde")
            mapping["1.6 -> 1"] = (1, None)  # "Taper opkomst start")
            mapping["2 -> 1.6"] = (1, "TaperDivergentie")  # eigenlijk 2 stroken breed, maar niet zo geregistreerd
            mapping["1.6 -> 2"] = (2, "TaperConvergentie")  # wel 2 stroken breed, want 2 breed bij start
        return mapping

    def __get_coords_from_csv(self, location: str) -> dict[str, float]:
        """
        Load the extent coordinates of the specified location from the csv file.
        Args:
            location (str): The name of the location.
        Returns:
            dict: The extent coordinates (north, east, south, west).
        Raises:
            ValueError: If the specified location is not found in the csv file.
            FileNotFoundError: If the file in the location of the filepath is not found.
            ValueError: If there is an error reading the csv file.
        """
        try:
            with open(self.__locations_csv_path, "r") as file:
                csv_reader = csv.DictReader(file, delimiter=";")
                for row in csv_reader:
                    if row["locatie"] == location:
                        return {
                            "noord": float(row["noord"]),
                            "oost": float(row["oost"]),
                            "zuid": float(row["zuid"]),
                            "west": float(row["west"]),
                        }
            raise ValueError(f"Ongeldige locatie: '{location}'. Voer een geldige naam van een locatie in.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Bestand niet gevonden: {self.__locations_csv_path}")
        except csv.Error as e:
            raise ValueError(f"Fout bij het lezen van het csv bestand: {e}")

    def __load_dataframes(self) -> None:
        """
        Load GeoDataFrames for each layer based on the specified location.
        """
        logger.info(f"{len(self.__FILE_PATHS)} lagen worden geladen...")
        for file_path in self.__FILE_PATHS:
            df_layer_name = self.__get_layer_name(file_path)
            logger.debug(f"Laag '{df_layer_name}' laden...")
            self.data[df_layer_name] = self.__load_dataframe(file_path)
            self.__edit_columns(df_layer_name)

    def __load_dataframe(self, file_path: str) -> gpd.GeoDataFrame:
        """
        Load the extent-intersecting parts of a GeoDataFrame from a shapefile.
        Args:
            file_path (str): The path to the shapefile.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with selected data.
        """
        return gpd.read_file(file_path, bbox=self.extent)

    @staticmethod
    def __get_layer_name(file_path) -> str:
        """
        Extract the layer name from the file path. The folder name is extracted and used
        as the layer name. Works well with the file paths in the original WEGGEG files.
        Args:
            file_path (str): The path to the file.
        Returns:
            str: The layer name.
        """
        parts = file_path.split("/")
        folder_name = parts[-2]
        return folder_name

    def __filter_multilinestring(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Filters a dataframe by MultiLineString registrations, after
        attempting to join convert to LineStrings."""
        s1 = len(dataframe)

        # Try to convert any MultiLineStrings to LineStrings.
        # dataframe.loc[:, "geometry"] = dataframe["geometry"].apply(lambda geom: self.__convert_to_linestring(geom)
        #                                                            if isinstance(geom, MultiLineString) else geom)

        # Filter so only entries are imported where the geometry column contains a LineString or Point
        dataframe = dataframe[dataframe["geometry"].apply(lambda x: isinstance(x, (LineString, Point)))]

        s2 = len(dataframe)

        if s1 - s2 > 0:
            logger.debug(f"Aantal MultiLineString registraties verwijderd: {s1 - s2}")

        return dataframe

    def __edit_line_registration_columns(self, dataframe: pd.DataFrame, name) -> pd.DataFrame:
        df = dataframe.copy()
        # All "stroken" dataframes have VNRWOL columns which should be converted to integer.
        df.loc[:, "VNRWOL"] = pd.to_numeric(df["VNRWOL"], errors="coerce").astype("Int64")

        if name == "Rijstroken":
            df.loc[:, "VOLGNRSTRK"] = pd.to_numeric(df["VOLGNRSTRK"], errors="raise").astype("Int64")
            df.loc[:, "LANE_INFO"] = df.apply(self.__get_lane_info, args=("OMSCHR",), axis=1)

        if name == "Kantstroken":
            # "Redresseerstrook", "Bushalte", "Pechhaven" and such are not considered.
            df = df[df["OMSCHR"].isin(["Vluchtstrook", "Puntstuk", "Spitsstrook", "Plusstrook"])]

        if name == "Mengstroken":
            df["LANE_INFO"] = df.apply(self.__get_lane_info, args=("AANT_MSK",), axis=1)

        return df

    def __edit_point_registration_columns(self, dataframe: pd.DataFrame, name) -> pd.DataFrame:
        df = dataframe.copy()
        if name == "Convergenties":
            df["TYPE"] = df["TYPE_CONV"].apply(lambda entry: self.__VERGENCE_NAME_MAPPING[entry])

        if name == "Divergenties":
            df["TYPE"] = df["TYPE_DIV"].apply(lambda entry: self.__VERGENCE_NAME_MAPPING[entry])

        if name == "Rijstrooksignaleringen":
            df = df[df["CODE"] == "KP"]  # Select only the KP (kruis-pijl) signaling (same as AU)
            df = df.assign(TYPE="Signalering")

        return df

    def __edit_columns(self, name: str) -> None:
        """
        Edits columns of GeoDataFrames in self.data in place.
        Args:
            name (str): The name of the GeoDataFrame.
        """
        df = self.data[name]

        df = self.__filter_multilinestring(df)

        if "stroken" in name:
            df = self.__edit_line_registration_columns(df, name)
        elif name == "Wegvakken":
            # Few registrations in shivi-netwerk don't have BEGINKM. These can be ignored.
            df = df.dropna(subset=["BEGINKM"])
        else:
            df = self.__edit_point_registration_columns(df, name)

        # Assign dataframe back to original data variable.
        self.data[name] = df

    def __get_lane_info(self, row, column):
        if row["KANTCODE"] == "H":
            return self.__lane_mapping_h.get(row[column], (0, None))
        else:
            return self.__lane_mapping_t.get(row[column], (0, None))

    @staticmethod
    def __convert_to_linestring(geom: MultiLineString) -> MultiLineString | LineString:
        """
        WIP function. This function should attempt to fix as many MultiLineString registrations as possible.
        """
        merged = line_merge(geom)
        if isinstance(merged, LineString):
            return merged

        # # Catching a specific case where there is a slight mismatch in the endpoints of a MultiLineString
        # if get_num_geometries(geom) == 2:
        #     line1 = geom.geoms[0]
        #     line1_points = [line1.coords[0], line1.coords[1], line1.coords[-2], line1.coords[-1]]
        #
        #     line2 = geom.geoms[1]
        #     line2_points = [line2.coords[0], line2.coords[1], line2.coords[-2], line2.coords[-1]]
        #
        #     common_points = [point for point in line1_points if point in line2_points]
        #     if len(common_points) == 0:
        #         logger.debug(f"Onverbonden MultiLineString wordt overgeslagen: {line1} en {line2}")
        #         return geom
        #
        #     assert not len(common_points) > 1, f"Meer dan één punt gemeen tussen {line1} en {line2}: {common_points}"
        #
        #     common_point = common_points[0]
        #     index_line1 = line1_points.index(common_point)
        #     index_line2 = line2_points.index(common_point)
        #
        #     if index_line1 == 1:
        #         line1 = LineString([coord for coord in line1.coords if coord != line1_points[0]])
        #     if index_line1 == 2:
        #         line1 = LineString([coord for coord in line1.coords if coord != line1_points[-1]])
        #     if index_line2 == 1:
        #         line2 = LineString([coord for coord in line2.coords if coord != line2_points[0]])
        #     if index_line2 == 2:
        #         line2 = LineString([coord for coord in line2.coords if coord != line2_points[-1]])
        #
        #     return line_merge(MultiLineString([line1, line2]))

        logger.debug(f"Omzetting naar LineString niet mogelijk (meer dan 2 geoms) voor {geom}")
        return geom


class WegModel:
    """
    A class for loading GeoDataFrames from shapefiles based on a specified location extent.

    Public attributes:
        extent (box): The extent of the specified location.
        points (dict): Points in the road model, indexed by ID.
        sections (dict): Sections in the road model, indexed by ID.
    """

    # The order of the layer names given here dictates the loading order. The first two are fixed.
    # It is important to import all layers with line geometries first, then point geometries.
    __LAYER_NAMES = [
        "Wegvakken",  # Used as 'reference layer'
        "Rijstroken",  # Used as 'initial layer'
        "Mengstroken", "Kantstroken", "Maximum snelheid",  # Contain line geometries
        "Rijstrooksignaleringen", "Convergenties", "Divergenties"  # Contain point geometries
    ]

    __MAIN_LANE_TYPES = ["Rijstrook", "Splitsing", "Samenvoeging", "Spitsstrook", "Plusstrook", "Weefstrook"]

    def __init__(self, dfl: DataFrameLader):
        """
        Initialise road model, loading data from the provided DataFrameLader object.
        Args:
            dfl (DataFrameLader): The dataframe loader object from which the road model should obtain data.
        Example:
            roadmodel = Wegmodel(DataFrameLader("Vught"))
        """
        self.__dfl = dfl
        self.extent = self.__dfl.extent

        self.__reference = {}
        self.__reference_index = 0
        self.sections = {}
        self.__section_index = 0
        self.__points = {}
        self.__point_index = 0

        self.__has_reference_layer = False
        self.__has_initial_layer = False

        self.__import_all_dataframes()
        self.__post_process_data()

    def __import_all_dataframes(self) -> None:
        """
        Load road attributes from all DataFrames.
        Note:
            The "wegvakken" layer from the shivi subset of WEGGEG is the
            first layer to be imported because these statements hold for it:
                1) it is defined everywhere where it would be necessary.
                2) it does not have internal overlap.
                3) It is a reliable source for roadside and travel_direction.
                4) It contains the hectoletter.
        """
        logger.info(f"{len(self.__LAYER_NAMES)} lagen worden verwerkt in het wegmodel...")
        for df_name in self.__LAYER_NAMES:
            logger.debug(f"Laag '{df_name}' wordt verwerkt in het wegmodel...")
            self.__import_dataframe(df_name)

    def __import_dataframe(self, df_name: str):
        """
        Load line and point features and their attributes from a GeoDataFrame.
        Args:
            df_name (str): Name of DataFrame to be imported.
        """
        dataframe = self.__dfl.data[df_name]
        for index, row in dataframe.iterrows():
            feature_info = self.__extract_row_properties(row, df_name)

            if not self.__has_reference_layer:
                self.__add_reference(feature_info)
                continue

            if not self.__has_initial_layer:
                self.__add_initial_section(feature_info)
                continue

            if isinstance(feature_info.pos_eigs.geometrie, Point):
                self.__add_point(feature_info)
            elif isinstance(feature_info.pos_eigs.geometrie, LineString):
                self.__merge_section(feature_info)
            else:
                logger.warning(f"Het volgende wordt niet toegevoegd. Controleer dit onderdeel in WEGGEG-data:\n{row}")

        if df_name == "Wegvakken":
            self.__has_reference_layer = True
        if df_name == "Rijstroken":
            self.__has_initial_layer = True

    def __extract_row_properties(self, row: pd.Series, name: str) -> ObjectInfo:
        """
        Turns the contents of a GeoDataframe row into a dictionary with the relevant entries.
        Args:
            row (pd.Series): Row containing information about the road section
            name (str): Name of dataframe.
        """
        if isinstance(row["geometry"], (Point, MultiPoint)):
            return self.__extract_point_properties(row, name)
        else:
            return self.__extract_line_properties(row, name)

    def __extract_point_properties(self, row: pd.Series, name: str) -> ObjectInfo:
        """
        Determines point info based on a row in the dataframe
        Args:
            row (Series): Dataframe row contents
            name (str): Dataframe name
        Returns:
            Point info in generalised dict format.
        """
        point_info = ObjectInfo(lijn=False)

        if not isinstance(row["geometry"], Point):
            logger.debug(f"Data bevat geen simpele puntgeometrie:\n{row}")
            return point_info

        section_info = self.get_one_section_at_point(row["geometry"])

        if not section_info:
            logger.debug(f"Punt in data overlapt niet met secties:\n{row}")
            return point_info

        point_info.pos_eigs.rijrichting = section_info.pos_eigs.rijrichting
        point_info.pos_eigs.wegnummer = section_info.pos_eigs.wegnummer
        point_info.pos_eigs.hectoletter = section_info.pos_eigs.hectoletter

        point_info.pos_eigs.km = round(row["KMTR"], 3)
        point_info.pos_eigs.geometrie = row["geometry"]
        point_info.obj_eigs["Type"] = row["TYPE"]

        if name == "Rijstrooksignaleringen":
            point_info.obj_eigs["Rijstrooknummers"] = [int(char) for char in row["RIJSTRKNRS"]]

        return point_info

    @staticmethod
    def __extract_line_properties(row: pd.Series, name: str) -> ObjectInfo:
        """
        Determines line info based on a row in the dataframe
        Args:
            row (Series): Dataframe row contents
            name (str): Dataframe name
        Returns:
            Line info in generalised dict format.
        """
        section_info = ObjectInfo(lijn=True)

        if not isinstance(row["geometry"], LineString):
            logger.warning(f"Data bevat geen simpele puntgeometrie:\n{row}")
            return section_info

        section_info.pos_eigs.km = [round(min(row["BEGINKM"], row["EINDKM"]), 3),
                                    round(max(row["BEGINKM"], row["EINDKM"]), 3)]
        section_info.pos_eigs.geometrie = set_precision(row["geometry"], CALCULATION_PRECISION)

        if name == "Wegvakken":
            section_info.pos_eigs.wegnummer = row["WEGNR_HMP"]
            if row["HECTO_LTTR"]:
                section_info.pos_eigs.hectoletter = row["HECTO_LTTR"]

        elif name == "Rijstroken":
            section_info.pos_eigs.rijrichting = row["IZI_SIDE"]

            # Flip range only if travel_direction is L.
            if section_info.pos_eigs.rijrichting == "L":
                section_info.pos_eigs.km = [round(row["EINDKM"], 3), round(row["BEGINKM"], 3)]

            first_lane_number = row["VNRWOL"]
            n_lanes, special = row["LANE_INFO"]

            # Indicate lane number and type of lane. Example: {1: "Rijstrook", 2: "Rijstrook"}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                section_info.obj_eigs[lane_nr] = "Rijstrook"

            # Take note of special circumstances on this feature.
            if special:
                lane_nr_special = row["VOLGNRSTRK"]
                section_info.obj_eigs["Special"] = (special, lane_nr_special)

        elif name == "Kantstroken":
            # Indicate lane number and type of kantstrook. Example: {3: "Spitsstrook"}
            lane_number = row["VNRWOL"]
            section_info.obj_eigs[lane_number] = row["OMSCHR"]
            if row["MAX_SNELH"]:
                section_info.obj_eigs["Maximumsnelheid_Open_Spitsstrook"] = row["MAX_SNELH"]

        elif name == "Mengstroken":
            first_lane_number = row["VNRWOL"]
            n_lanes, special = row["LANE_INFO"]

            # Indicate lane number and type of lane. Example: {4: "Weefstrook"}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                section_info.obj_eigs[lane_nr] = row["OMSCHR"]

            # Take note of special circumstances on this feature.
            if special:
                section_info.obj_eigs["Special"] = (special, first_lane_number)

        elif name == "Maximum snelheid":
            if (not row["BEGINTIJD"] or math.isnan(row["BEGINTIJD"])
                    or row["BEGINTIJD"] == 19):
                section_info.obj_eigs["Maximumsnelheid"] = row["OMSCHR"]
            elif row["BEGINTIJD"] == 6:
                section_info.obj_eigs["Maximumsnelheid_Beperkt_Overdag"] = row["OMSCHR"]
            else:
                raise Exception(f"Deze begintijd is niet in het model verwerkt: {row['BEGINTIJD']}")

        return section_info

    def __merge_section(self, new_info: ObjectInfo) -> None:
        """
        Merges the given section with existing sections in self.sections, by iteratively
        partioning the geometry and km-registrations and applying the relevant properties.
        Args:
            new_info (ObjectInfo): Information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_info)

        if not overlap_sections:
            logger.warning(f"{new_info} heeft geen overlap met het wegmodel. "
                           f"Op deze positie is waarschijnlijk niets geregistreerd, of de registratie "
                           f"is een MultiLineString, welke niet wordt meegenomen in het wegmodel.")
            return

        first_time = True
        reverse_overlap_geom = False

        for other_section_index, other_section_data in overlap_sections.items():
            other_info = other_section_data[0]
            overlap_geometry = other_section_data[1]

            if first_time:
                # Align new section range and geometry according to other section. This only needs to be done once,
                # assuming that all other sections already in the road model have the same orientation (which they do).
                if other_info.pos_eigs.rijrichting == "L":
                    new_info.pos_eigs.km.reverse()
                if not same_direction(other_info.pos_eigs.geometrie, new_info.pos_eigs.geometrie):
                    new_info.pos_eigs.geometrie = reverse(new_info.pos_eigs.geometrie)
                    reverse_overlap_geom = True
                    logger.debug("Pay attention: geometries reversed.")
                first_time = False

            if reverse_overlap_geom:
                overlap_geometry = reverse(overlap_geometry)

            logger.debug(f"Overlap tussen {new_info} en wegmodel sectie {other_section_index}: {other_info}")

            linedist_overlap_start_on_other = line_locate_point(other_info.pos_eigs.geometrie, Point(overlap_geometry.coords[0]), normalized=True)
            linedist_overlap_end_on_other = line_locate_point(other_info.pos_eigs.geometrie, Point(overlap_geometry.coords[-1]), normalized=True)
            linedist_other_start_on_overlap = line_locate_point(overlap_geometry, Point(other_info.pos_eigs.geometrie.coords[0]), normalized=True)
            linedist_other_end_on_overlap = line_locate_point(overlap_geometry, Point(other_info.pos_eigs.geometrie.coords[-1]), normalized=True)

            # logger.debug(
            #     f"Check: {new_info.pos_eigs.geometrie}\n{overlap_geometry}\n{other_info.pos_eigs.geometrie}")
            # logger.debug(f"See {linedist_overlap_start_on_other}, {linedist_overlap_end_on_other} "
            #              f"{linedist_other_start_on_overlap} {linedist_other_end_on_overlap}")

            TINY_DEVIATION_LOW = 0.001
            TINY_DEVIATION_HIGH = 0.999

            startpoint_overlap = linedist_overlap_start_on_other < TINY_DEVIATION_LOW and linedist_other_start_on_overlap < TINY_DEVIATION_LOW
            endpoint_overlap = linedist_overlap_end_on_other > TINY_DEVIATION_HIGH and linedist_other_end_on_overlap > TINY_DEVIATION_HIGH
            overlap_ends_earlier = linedist_overlap_end_on_other < TINY_DEVIATION_HIGH
            overlap_starts_later = linedist_overlap_start_on_other > TINY_DEVIATION_LOW

            # Case 1: overlap_geometry == other_info, the road model section is completely covered by the new section
            # Alternatively: self.__check_geometry_equality(other_info.pos_eigs.geometrie, overlap_geometry)
            if startpoint_overlap and endpoint_overlap:
                logger.debug("This overlap falls under case 1")
                self.__update_section(other_section_index, new_obj_eigs=new_info.obj_eigs)

            # Case 2: overlap and road model section start at the same point, but overlap ends earlier
            elif startpoint_overlap and overlap_ends_earlier:
                logger.debug("This overlap falls under case 2")
                remainder_geometry = self.__get_first_remainder(other_info.pos_eigs.geometrie, overlap_geometry)
                other_properties = deepcopy(other_info.obj_eigs)
                km_registrations = [
                    other_info.pos_eigs.km[0],
                    new_info.pos_eigs.km[1],
                    new_info.pos_eigs.km[1],
                    other_info.pos_eigs.km[1]
                ]
                if km_registrations[2] == km_registrations[3]:
                    logger.warning(f"Fout in de verwerking of in de km-registraties van {new_info} / {other_info}.")

                self.__update_section(other_section_index,
                                      new_km=[km_registrations[0], km_registrations[1]],
                                      new_obj_eigs=new_info.obj_eigs,
                                      new_geom=overlap_geometry)
                self.__add_section(
                    ObjectInfo(
                        pos_eigs=PositieEigenschappen(
                            rijrichting=other_info.pos_eigs.rijrichting,
                            wegnummer=other_info.pos_eigs.wegnummer,
                            hectoletter=other_info.pos_eigs.hectoletter,
                            km=[km_registrations[2], km_registrations[3]],
                            geometrie=remainder_geometry),
                        obj_eigs=other_properties)
                )

            # Case 3: overlap and road model section end at the same point, but overlap starts later
            elif endpoint_overlap and overlap_starts_later:
                logger.debug("This overlap falls under case 3")
                remainder_geometry = self.__get_first_remainder(other_info.pos_eigs.geometrie, overlap_geometry)
                other_properties = deepcopy(other_info.obj_eigs)

                km_registrations = [
                    other_info.pos_eigs.km[0],
                    new_info.pos_eigs.km[0],
                    new_info.pos_eigs.km[0],
                    other_info.pos_eigs.km[1]
                ]
                if km_registrations[0] == km_registrations[1]:
                    logger.warning(f"Fout in de verwerking of in de km-registraties van {new_info} / {other_info}.")

                self.__add_section(
                    ObjectInfo(
                        pos_eigs=PositieEigenschappen(
                            rijrichting=other_info.pos_eigs.rijrichting,
                            wegnummer=other_info.pos_eigs.wegnummer,
                            hectoletter=other_info.pos_eigs.hectoletter,
                            km=[km_registrations[0], km_registrations[1]],
                            geometrie=remainder_geometry),
                        obj_eigs=other_properties)
                )
                self.__update_section(other_section_index,
                                      new_km=[km_registrations[2], km_registrations[3]],
                                      new_obj_eigs=new_info.obj_eigs,
                                      new_geom=overlap_geometry)

            # Case 4: the overlap start and end are encased by the road model section
            elif overlap_ends_earlier and overlap_starts_later:
                logger.debug("This overlap falls under case 4")
                remainder_geometries = self.__get_remainders(other_info.pos_eigs.geometrie, overlap_geometry)
                other_properties = deepcopy(other_info.obj_eigs)
                km_registrations = [
                    other_info.pos_eigs.km[0],
                    new_info.pos_eigs.km[0],
                    new_info.pos_eigs.km[1],
                    other_info.pos_eigs.km[1]
                ]
                if km_registrations[0] == km_registrations[1] or km_registrations[2] == km_registrations[3]:
                    logger.warning(f"Fout in de verwerking of in de km-registraties van {new_info} / {other_info}.")

                self.__add_section(
                    ObjectInfo(
                        pos_eigs=PositieEigenschappen(
                            rijrichting=other_info.pos_eigs.rijrichting,
                            wegnummer=other_info.pos_eigs.wegnummer,
                            hectoletter=other_info.pos_eigs.hectoletter,
                            km=[km_registrations[0], km_registrations[1]],
                            geometrie=remainder_geometries[0]),
                        obj_eigs=other_properties)
                )
                self.__update_section(other_section_index,
                                      new_km=[km_registrations[1], km_registrations[2]],
                                      new_obj_eigs=new_info.obj_eigs,
                                      new_geom=overlap_geometry)
                self.__add_section(
                    ObjectInfo(
                        pos_eigs=PositieEigenschappen(
                            rijrichting=other_info.pos_eigs.rijrichting,
                            wegnummer=other_info.pos_eigs.wegnummer,
                            hectoletter=other_info.pos_eigs.hectoletter,
                            km=[km_registrations[2], km_registrations[3]],
                            geometrie=remainder_geometries[1]),
                        obj_eigs=other_properties)
                )

            else:
                logger.warning(f"Not sure how to handle this case: {new_info} {other_info}.")
                logger.warning(f"Geometries: {new_info.pos_eigs.geometrie} {other_info.pos_eigs.geometrie}.")
                logger.warning(f"See {linedist_overlap_start_on_other}, {linedist_overlap_end_on_other} {linedist_other_start_on_overlap} {linedist_other_end_on_overlap}")

    def __get_remainders(self, geom1, geom2) -> list[LineString]:
        assert geom1 and not is_empty(geom1), f"Geometrie is leeg: {geom1}. Kloppen de km-registraties?"
        assert geom2 and not is_empty(geom2), f"Geometrie is leeg: {geom2}. Kloppen de km-registraties?"
        assert isinstance(geom1, LineString), f"Kan niet werken met MultiLineString registratie: {geom1}"
        assert isinstance(geom2, LineString), f"Kan niet werken met MultiLineString registratie: {geom2}"

        if self.__check_geometry_equality(geom1, geom2):
            raise AssertionError(f"Geometrieën zijn exact aan elkaar gelijk:\n"
                                 f"{geom1}\n{geom2}\n"
                                 f"Zijn de kilometerregistraties juist?\n")

        geom1 = set_precision(geom1, CALCULATION_PRECISION)
        geom2 = set_precision(geom2, CALCULATION_PRECISION)
        remainders = difference(geom1, geom2, grid_size=CALCULATION_PRECISION)

        if isinstance(remainders, LineString) and not remainders.is_empty:
            return [remainders]
        elif isinstance(remainders, MultiLineString) and not remainders.is_empty:
            return [geom for geom in remainders.geoms]
        else:
            raise Exception(f"Could not determine the remainders between\n{geom1}\nand {geom2}")

    def __get_first_remainder(self, geom1: LineString, geom2: LineString) -> LineString:
        """
        Finds the first geometry that two Shapely LineStrings do NOT have in common.
        Args:
            geom1 (LineString): The first Shapely LineString.
            geom2 (LineString): The second Shapely LineString.
        Returns:
            A LineString describing the difference geometry between the two
            provided sections. If there are two options, the first remainder
            option is returned, based on the directional order of geom1.
        """
        remainders = self.__get_remainders(geom1, geom2)

        if len(remainders) == 1 and not remainders[0].is_empty:
            return set_precision(remainders[0], CALCULATION_PRECISION)
        elif len(remainders) > 1 and not remainders[0].is_empty:
            # TODO: Determine more reliable method to extract the correct diff here!
            start_point_geom1, end_point_geom1 = get_endpoints(geom1)
            start_point_geom2, end_point_geom2 = get_endpoints(geom2)

            selected_diff = LineString()

            for geom in remainders:
                start_point_remainder, end_point_remainder = get_endpoints(geom)
                passes = (dwithin(start_point_remainder, start_point_geom1, 3*DISTANCE_TOLERANCE) or
                          dwithin(start_point_remainder, end_point_geom1, 3*DISTANCE_TOLERANCE) and
                          dwithin(end_point_remainder, end_point_geom2, 3*DISTANCE_TOLERANCE) or
                          dwithin(start_point_remainder, end_point_geom2, 3*DISTANCE_TOLERANCE) and
                          dwithin(end_point_remainder, end_point_geom1, 3*DISTANCE_TOLERANCE))
                if passes:
                    logger.info(f"I would select {geom}")
                    selected_diff = geom
                    break

            if is_empty(selected_diff):
                # By default, select the first geometry (directional order of geom1 is maintained)
                logger.warning(f"I have no clue based on {start_point_geom1} {end_point_geom1}-{end_point_geom2} and {remainders}, so I will pick the first remaining geometry.")
                selected_diff = remainders[0]
                logger.warning(f"I picked {selected_diff}")

            # if get_num_geometries(remainders) > 2:
            #     logger.warning(f"Meer dan 2 geometrieën resterend. Extra geometrieën: {remainders.geoms}")

            return set_precision(selected_diff, CALCULATION_PRECISION)
        else:
            logger.warning(f"Lege of onjuiste overgebleven geometrie ({remainders}) tussen\n"
                           f"{geom1} en \n{geom2}")
            return set_precision(remainders, CALCULATION_PRECISION)

    @staticmethod
    def __check_geometry_equality(geom1: LineString, geom2: LineString) -> bool:
        """
        Performs various checks to determine whether two LineString geometries are equal.
        Args:
            geom1 (LineString): First LineString to be compared.
            geom2 (LineString): Second LineString to be compared.
        Returns:
            Boolean indicating whether the geometries can be considered equal.
        """
        if equals(geom1, geom2):
            return True

        # Geometries that have Points with very close but not identical coordinates...
        if equals_exact(geom1, geom2, tolerance=DISTANCE_TOLERANCE):
            return True

        # Geometries with a different amount of vertices... (compare their simplified versions)
        simplified_geom1 = simplify(geom1, 0.1, preserve_topology=False)
        simplified_geom2 = simplify(geom2, 0.1, preserve_topology=False)
        if equals_exact(simplified_geom1, simplified_geom2, tolerance=DISTANCE_TOLERANCE):
            return True

        return False

    @staticmethod
    def __get_overlap(pos1: PositieEigenschappen, pos2: PositieEigenschappen) -> LineString | None:
        """
        Finds the overlap geometry between two sections by their positional properties.
        Args:
            pos1 (PositieEigenschappen): The first section position properties.
            pos2 (PositieEigenschappen): The second section position properties.
        Returns:
            LineString describing the overlap geometry.
            Returns None if there is no overlap geometry.
        Note:
            The function uses the `intersection` method from Shapely to compute the overlap between
            the two LineString geometries. If the geometries do not overlap or have only a Point of
            intersection, the function returns None.
        """
        # First, check whether the sections have an overlapping range at all, which
        # means the more complex intersection() function doesn't need to be called.
        if not determine_range_overlap(pos1.km, pos2.km):
            return None

        # Then, check if the overlap between the geometries is of the same dimension as the geometries.
        # if not overlaps(pos1.geometrie, pos2.geometrie):
        #     return None

        overlap_geometry = intersection(pos1.geometrie, pos2.geometrie, grid_size=CALCULATION_PRECISION)

        # Attempt to convert to linestring if necessary
        if isinstance(overlap_geometry, MultiLineString) and not overlap_geometry.is_empty:
            overlap_geometry = line_merge(overlap_geometry)

        if not isinstance(overlap_geometry, LineString) or overlap_geometry.is_empty or overlap_geometry.length < 0.1:
            return None

        # Catch code in case the first point or the last point of the geometries overlap,
        # but is not added to the overlap geometry due to precision errors
        if (dwithin(Point(pos1.geometrie.coords[0]), Point(pos2.geometrie.coords[0]), DISTANCE_TOLERANCE) and not
        dwithin(Point(pos1.geometrie.coords[0]), Point(overlap_geometry.coords[0]), DISTANCE_TOLERANCE)):
            overlap_geometry = LineString([pos1.geometrie.coords[0]] + [coord for coord in overlap_geometry.coords])

        if (dwithin(Point(pos1.geometrie.coords[-1]), Point(pos2.geometrie.coords[-1]), DISTANCE_TOLERANCE) and not
                dwithin(Point(pos1.geometrie.coords[-1]), Point(overlap_geometry.coords[-1]), DISTANCE_TOLERANCE)):
            overlap_geometry = LineString([coord for coord in overlap_geometry.coords] + [pos1.geometrie.coords[-1]])

        return set_precision(overlap_geometry, CALCULATION_PRECISION)

    def __remove_sections(self, indices: set[int]) -> None:
        """
        Removes sections at the given indices.
        Args:
            indices (set): Set of indices at which to remove sections.
        """
        for index in indices:
            logger.debug(f"Sectie {index} verwijderd.")
            self.sections.pop(index)

    def __remove_points(self, indices: set[int]) -> None:
        """
        Removes points at the given indices.
        Args:
            indices (set): Set of indices at which to remove points.
        """
        for index in indices:
            logger.debug(f"Punt {index} verwijderd: {self.__points[index]}.")
            self.__points.pop(index)

    def __update_section(self, index: int,
                         new_km: list = None, new_obj_eigs: dict = None, new_geom: LineString = None) -> None:
        """
        Updates one or more properties of a section at a given index.
        Args:
            index (int): Index of section to be updated
            new_km (list[float]): Start and end registration kilometre.
            new_obj_eigs (dict): All properties that belong to the section.
            new_geom (LineString): The geometry of the section.
        Logs:
            Changed section properties.
        """
        assert any([new_km, new_obj_eigs, new_geom]), "Update section aangeroepen, maar er is geen update nodig."
        assert new_km and new_geom or not (new_km or new_geom), \
            "Als de geometrie wordt aangepast, moet ook het bereik worden bijgewerkt. Dit geldt ook andersom."

        if new_km:
            self.sections[index].pos_eigs.km = new_km
        if new_obj_eigs:
            self.sections[index].obj_eigs = self.__merge_lane_dicts(self.sections[index], new_obj_eigs)
        if new_geom:
            self.sections[index].pos_eigs.geometrie = new_geom

        self.__log_section(index, True)

    @staticmethod
    def __merge_lane_dicts(roadmodel_section, dict_new):
        dict_model = roadmodel_section.obj_eigs
        lane_numbers_1 = [key for key in dict_model.keys() if isinstance(key, int)]
        lane_numbers_2 = [key for key in dict_new.keys() if isinstance(key, int)]

        overlap_numbers = [key for key in lane_numbers_1 if key in lane_numbers_2]

        if overlap_numbers:
            logger.debug(f"Overlappende rijstrooknummers {overlap_numbers} tussen {dict_model} en {dict_new}.")

            change_made = False
            overlap_number = overlap_numbers[0]
            if dict_new[overlap_number] in ["Vluchtstrook", "Uitrijstrook", "Splitsing"]:
                dict_new = {lane_nr + 1: lane_type for lane_nr, lane_type in dict_new.items() if isinstance(lane_nr, int)}
                change_made = True

            if change_made:
                logger.debug(f"Overlap aangepakt door vluchtstrook op te schuiven: {dict_new}")
            else:
                logger.warning(f"Onopgeloste overlappende rijstrooknummers {overlap_numbers} "
                               f"tussen {dict_model} en {dict_new}. Dit gebeurt voor {roadmodel_section.pos_eigs}.")

        return {**dict_model, **dict_new}

    def __add_section(self, new_section: ObjectInfo) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (ObjectInfo): Information class for new section.
        Logs:
            Newly added section properties.
        """
        if not new_section.pos_eigs.geometrie or is_empty(new_section.pos_eigs.geometrie):
            logger.warning(f"Poging om een lege lijngeometrie toe te voegen: {new_section.pos_eigs.geometrie}")
            return

        if isinstance(new_section.pos_eigs.geometrie, MultiLineString):
            logger.warning(f"Een Multilinestring kan niet worden toegevoegd: {new_section.pos_eigs.geometrie}")
            return

        self.sections[self.__section_index] = new_section
        self.__log_section(self.__section_index, False)
        self.__section_index += 1

    def __add_initial_section(self, section_info: ObjectInfo) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Does NOT check for overlap with other features.
        Args:
            section_info (ObjectInfo): Initial section info
        Logs:
            Newly added section properties.
        """
        reference_info = self.__get_overlapping_reference_info(section_info)

        if not reference_info:
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            logger.debug(f"{section_info} heeft geen overlap met de referentie-laag. "
                         f"Op deze positie is waarschijnlijk niets geregistreerd, of de registratie "
                         f"is een MultiLineString, welke niet wordt meegenomen in het wegmodel.")
            return

        # Ensure the kilometer registrations are oriented in driving direction.
        if section_info.pos_eigs.rijrichting == "L":
            section_info.pos_eigs.km = [max(section_info.pos_eigs.km), min(section_info.pos_eigs.km)]
        else:
            section_info.pos_eigs.km = [min(section_info.pos_eigs.km), max(section_info.pos_eigs.km)]

        # Ensure the first geometries are oriented in driving direction according to the reference layer.
        if not same_direction(reference_info.pos_eigs.geometrie, section_info.pos_eigs.geometrie):
            geom = reverse(section_info.pos_eigs.geometrie)
        else:
            geom = section_info.pos_eigs.geometrie

        self.__add_section(
            ObjectInfo(
                pos_eigs=PositieEigenschappen(
                    rijrichting=section_info.pos_eigs.rijrichting,
                    wegnummer=reference_info.pos_eigs.wegnummer,
                    hectoletter=reference_info.pos_eigs.hectoletter,
                    km=section_info.pos_eigs.km,
                    geometrie=geom),
                obj_eigs=section_info.obj_eigs)
        )

    def __add_reference(self, reference_info: ObjectInfo) -> None:
        """
        Adds a feature to the reference variable and increases the index.
        Args:
            reference_info (ObjectInfo): Info of new reference feature to add to reference layer.
        Logs:
            Newly added reference feature properties.
        """
        assert not is_empty(reference_info.pos_eigs.geometrie), \
            f"Poging om een lege lijngeometrie toe te voegen: {reference_info}"

        self.__reference[self.__reference_index] = reference_info
        self.__log_reference(self.__reference_index)
        self.__reference_index += 1

    def __add_point(self, point_info: ObjectInfo) -> None:
        """
        Adds a point to the points variable and increases the index.
        Args:
            point_info (ObjectInfo): Point info to be added.
        Logs:
            Newly added point properties.
        """
        assert not is_empty(point_info.pos_eigs.geometrie), \
            f"Poging om een lege puntgeometrie toe te voegen: {point_info}"

        self.__points[self.__point_index] = point_info
        self.__log_point(self.__point_index)
        self.__point_index += 1

    def __log_point(self, index: int) -> None:
        """
        Logs addition of point in self.points at given index.
        Args:
            index (int): Index of point to log info for.
        """
        logger.debug(f"Punt {index} toegevoegd: \t"
                     f"{self.__points[index]} en geometrie:\t"
                     f"{self.__points[index].pos_eigs.geometrie}")

    def __log_reference(self, index: int) -> None:
        """
        Logs addition of section in self.__reference at given index.
        Args:
            index (int): Index of section to log info for.
        """
        logger.debug(f"Referentie {index} toegevoegd:   \t"
                     f"{self.__reference[index].pos_eigs.wegnummer}\t"
                     f"{self.__reference[index].pos_eigs.hectoletter}\t"
                     f"{self.__reference[index].pos_eigs.geometrie}")

    def __log_section(self, index: int, changed: bool = False) -> None:
        """
        Logs change or addition for section in self.sections at given index.
        Args:
            index (int): Index of section to log info for.
        """
        wording = {True: "veranderd:  ", False: "toegevoegd: "}
        logger.debug(f"Sectie {index} {wording[changed]}\t"
                     f"{self.sections[index]} en {round(self.sections[index].pos_eigs.geometrie.length)} m geometrie:\t"
                     f"{self.sections[index].pos_eigs.geometrie}")

    def __get_overlapping_reference_info(self, section_info: ObjectInfo) -> ObjectInfo | None:
        """
        Finds the first overlapping geometry from the reference layer and returns it.
        Args:
            section_info (ObjectInfo): Section information for which the reference overlap should be determined.
        Returns:
            Feature info from the reference layer. If there is no overlap with the reference,
            then None is returned instead.
        """
        for reference_index, reference_info in self.__reference.items():
            if self.__get_overlap(section_info.pos_eigs, reference_info.pos_eigs):
                # Return the first one found (works fine for now).
                return reference_info
        return None

    def __get_overlapping_sections(self, section_info: ObjectInfo) -> dict:
        """
        Finds all sections within self which overlap with the provided section
        and returns them in a list.
        Args:
            section_info (ObjectInfo): All data pertaining to a section.
        Returns:
            A list of overlap section data, sorted by start_km depending on
            the driving direction of one of the other sections, which is assumed
            to be representative for all other sections.
        """
        overlapping_sections = {}
        for other_section_index, other_section_info in self.sections.items():
            overlap_geometry = self.__get_overlap(section_info.pos_eigs, other_section_info.pos_eigs)
            if overlap_geometry:
                overlapping_sections[other_section_index] = (other_section_info, overlap_geometry)
        return overlapping_sections

    def __post_process_data(self) -> None:
        sections_to_remove = set()
        for section_index, section_info in self.sections.items():
            # [1] Throw out sections that do not intersect the extent.
            if not intersection(section_info.pos_eigs.geometrie, self.__dfl.extent):
                sections_to_remove.add(section_index)
                continue

            # [2] Throw out sections that do not have at least one normal lane in them.
            if not [key for key in section_info.obj_eigs.keys() if section_info.obj_eigs[key] == "Rijstrook"]:
                sections_to_remove.add(section_index)
                continue

        self.__remove_sections(sections_to_remove)

        for section_index, section_info in self.sections.items():
            # [3] Special code to fill in lane registration gaps in the case of 'special' registrations.
            # Assumes there is only one special registration per section.
            if "Special" in section_info.obj_eigs.keys():  # and "Taper" in section_info.obj_eigs["Special"][0]:
                logger.debug(f"Consider {section_info.obj_eigs}")
                # Section has a singular lane registered for the taper
                lane_numbers = [key for key in section_info.obj_eigs.keys() if isinstance(key, int)]
                special_lane_nr = section_info.obj_eigs["Special"][1]

                if special_lane_nr not in section_info.obj_eigs.keys():  # In case special lane number is the unregistered lane
                    section_info.obj_eigs[special_lane_nr] = section_info.obj_eigs[special_lane_nr - 1]

                if special_lane_nr + 1 not in section_info.obj_eigs.keys():
                    if "Taper" in section_info.obj_eigs["Special"][0]:  # In case of gap or final lane
                        section_info.obj_eigs[special_lane_nr + 1] = section_info.obj_eigs[special_lane_nr]

                elif section_info.obj_eigs[special_lane_nr] != section_info.obj_eigs[special_lane_nr + 1]:
                    # Move lane registrations one lane to the right
                    for lane_number in range(max(lane_numbers), special_lane_nr - 1, -1):
                        section_info.obj_eigs[lane_number + 1] = section_info.obj_eigs[lane_number]

            # [4] Manual gap fix. Move lanes to fill the gap
            lane_numbers = [key for key in section_info.obj_eigs.keys() if isinstance(key, int)]
            gap_number = self.find_gap(lane_numbers)
            if gap_number:
                logger.debug(f"Sectie heeft een gat in registratie rijstroken op {gap_number}: {section_info}")
                lane_numbers = [key for key in section_info.obj_eigs.keys() if isinstance(key, int)]
                section_info.verw_eigs.heeft_verwerkingsfout = True

                for lane_number in range(gap_number, max(lane_numbers)):
                    section_info.obj_eigs[lane_number] = section_info.obj_eigs[lane_number + 1]
                section_info.obj_eigs.pop(max(lane_numbers))

                lane_numbers = [key for key in section_info.obj_eigs.keys() if isinstance(key, int)]

                if not self.find_gap(lane_numbers):
                    logger.debug(f"Gat opgelost: {section_info}")
                else:
                    logger.warning(f"Gat in registratie rijstroken {section_info} is niet opgelost. "
                                   f"Deze sectie wordt in de visualisatie doorzichtig weergegeven.")

        for section_index, section_info in self.sections.items():
            section_verw_eigs = LijnVerwerkingsEigenschappen()

            section_verw_eigs.heeft_verwerkingsfout = section_info.verw_eigs.heeft_verwerkingsfout

            skip_start_check = False
            skip_end_check = False

            start_point = Point(section_info.pos_eigs.geometrie.coords[0])
            end_point = Point(section_info.pos_eigs.geometrie.coords[-1])

            for point_info in self.get_points_info("*vergentie"):
                if point_info.pos_eigs.geometrie.dwithin(start_point, DISTANCE_TOLERANCE):
                    section_verw_eigs.vergentiepunt_start = True
                    section_verw_eigs.start_kenmerk = {key: value for key, value in section_info.obj_eigs.items()
                                                       if value in ["Invoegstrook", "Samenvoeging", "Weefstrook"]}
                    skip_start_check = True
                if point_info.pos_eigs.geometrie.dwithin(end_point, DISTANCE_TOLERANCE):
                    section_verw_eigs.vergentiepunt_einde = True
                    section_verw_eigs.einde_kenmerk = {key: value for key, value in section_info.obj_eigs.items()
                                                       if value in ["Uitrijstrook", "Splitsing", "Weefstrook"]}
                    skip_end_check = True

            start_sections = self.get_sections_by_point(start_point)
            end_sections = self.get_sections_by_point(end_point)

            main_up, div_up = self.__select_main_and_div(start_sections, section_index, section_info)
            main_down, div_down = self.__select_main_and_div(end_sections, section_index, section_info)

            section_verw_eigs.sectie_stroomopwaarts = main_up
            section_verw_eigs.sectie_stroomafwaarts = main_down
            section_verw_eigs.sectie_afbuigend_stroomopwaarts = div_up
            section_verw_eigs.sectie_afbuigend_stroomafwaarts = div_down

            if main_up and not skip_start_check:
                section_verw_eigs.start_kenmerk = (
                    self.__get_difference(section_info.obj_eigs, self.sections[main_up].obj_eigs))

            if main_down and not skip_end_check:
                section_verw_eigs.einde_kenmerk = (
                    self.__get_difference(section_info.obj_eigs, self.sections[main_down].obj_eigs))

            hoofdstrooknummers, strooknummers = self.get_lane_numbers(section_info.obj_eigs)
            strooknummers_links = [lane_nr for lane_nr in strooknummers if
                                   hoofdstrooknummers and lane_nr < min(hoofdstrooknummers)]
            strooknummers_rechts = [lane_nr for lane_nr in strooknummers if
                                    hoofdstrooknummers and lane_nr > max(hoofdstrooknummers)]

            section_verw_eigs.aantal_stroken = len(strooknummers)
            section_verw_eigs.aantal_hoofdstroken = len(hoofdstrooknummers)
            section_verw_eigs.aantal_rijstroken_links = len(strooknummers_links)
            section_verw_eigs.aantal_rijstroken_rechts = len(strooknummers_rechts)

            self.sections[section_index].verw_eigs = section_verw_eigs

        points_to_remove = set()
        for point_index, point_info in self.__points.items():
            point_verw_eigs = PuntVerwerkingsEigenschappen()

            overlapping_sections = self.get_sections_by_point(point_info.pos_eigs.geometrie)

            if not overlapping_sections:
                points_to_remove.add(point_index)
                continue

            sections_near_point = [section_id for section_id in overlapping_sections.keys()]
            point_verw_eigs.sectie_ids = sections_near_point

            # Get the local number of (main) lanes. Take the highest value if there are multiple.
            point_verw_eigs.aantal_stroken = (
                max(lane_info.verw_eigs.aantal_stroken for lane_info in overlapping_sections.values()))
            point_verw_eigs.aantal_hoofdstroken = (
                max(lane_info.verw_eigs.aantal_hoofdstroken for lane_info in overlapping_sections.values()))

            point_verw_eigs.lokale_hoek = self.__get_local_angle(sections_near_point, point_info.pos_eigs.geometrie)

            if point_info.obj_eigs["Type"] in ["Samenvoeging", "Invoeging"]:
                point_verw_eigs.ingaande_secties = \
                    [section_id for section_id, section_info in overlapping_sections.items()
                     if self.get_n_lanes(section_info.obj_eigs)[1] != point_verw_eigs.aantal_stroken]
                point_verw_eigs.uitgaande_secties = \
                    [section_id for section_id, section_info in overlapping_sections.items()
                     if self.get_n_lanes(section_info.obj_eigs)[1] == point_verw_eigs.aantal_stroken]

            if point_info.obj_eigs["Type"] in ["Splitsing", "Uitvoeging"]:
                point_verw_eigs.ingaande_secties = \
                    [section_id for section_id, section_info in overlapping_sections.items()
                     if self.get_n_lanes(section_info.obj_eigs)[1] == point_verw_eigs.aantal_stroken]
                point_verw_eigs.uitgaande_secties = \
                    [section_id for section_id, section_info in overlapping_sections.items()
                     if self.get_n_lanes(section_info.obj_eigs)[1] != point_verw_eigs.aantal_stroken]

            # Check if invoeging has 2 ingoing sections, check if uitvoeging has 2 outgoing sections!
            if (point_info.obj_eigs["Type"] in ["Samenvoeging", "Invoeging"]
                    and not (len(point_verw_eigs.ingaande_secties) == 2) or
                    (point_info.obj_eigs["Type"] in ["Splitsing", "Uitvoeging"]
                     and not len(point_verw_eigs.uitgaande_secties) == 2)):
                # This point should not be added at all. Remove it later.
                points_to_remove.add(point_index)

            self.__points[point_index].verw_eigs = point_verw_eigs

        self.__remove_points(points_to_remove)

    @staticmethod
    def __get_min_max_lane_number(lanes: dict) -> tuple[int, int]:
        lane_numbers = [lane_nr for lane_nr in lanes.keys() if isinstance(lane_nr, int)]
        return min(lane_numbers), max(lane_numbers)

    def __select_main_and_div(self, connecting_sections: dict, section_index: int,
                              section_info: ObjectInfo) -> tuple[int | None, int | None]:
        """
        When the road model splits into two sections, this function can separate the two
        connecting sections into the main section and the diverging section.
        It makes use of the puntstuk registrations and hectoletter difference.
        Because at this point in effect three sections come together, it is important to specify the
        section from which the split or merge is approached, so it can be excluded.
        Args:
            connecting_sections (dict): Index and object properties of connecting sections.
            section_index (int): Index of current section (the section which should be excluded).
            section_info (ObjectInfo): Properties of current section, to compare to.
        Returns:
            (main section index, diverging section index) as a tuple. In case there is no
            such section, the index is instead replaced by None.
        """
        connected = [index for index in connecting_sections.keys() if index != section_index]
        if len(connected) == 0:
            return None, None

        if len(connected) == 1:
            return connected[0], None

        adjacent_sections = {index: section for index, section in connecting_sections.items() if index != section_index}

        # If puntstuk itself, return section with same hectoletter.
        this_section_max_lane_nr = max([key for key in section_info.obj_eigs.keys() if isinstance(key, int)])
        if section_info.obj_eigs[this_section_max_lane_nr] == "Puntstuk":
            connected = [index for index, section in adjacent_sections.items() if
                         section_info.pos_eigs.hectoletter == section.pos_eigs.hectoletter]
            # If all hectoletters are the same, use the km registration.
            if len(connected) > 1:
                if section_info.pos_eigs.rijrichting == "L":
                    connected = [index for index, section in adjacent_sections.items() if
                                 section_info.pos_eigs.km[1] == section.pos_eigs.km[0]]
                if section_info.pos_eigs.rijrichting == "R":
                    connected = [index for index, section in adjacent_sections.items() if
                                 section_info.pos_eigs.km[0] == section.pos_eigs.km[1]]
            if len(connected) > 1:
                raise AssertionError("Meer dan één sectie lijkt kandidaat voor de hoofdbaan.")
            if len(connected) == 0:
                return None, None
            return connected[0], None

        assert len(adjacent_sections) == 2, ("Er moeten twee secties verbonden zijn aan een puntstuk.\n"
                                             f"Fout aangetroffen met sectie {section_index}: {section_info},\n"
                                             f"Verbonden secties: {connecting_sections}.\n"
                                             f"Aangrenzende secties: {adjacent_sections}")

        # If one of the other sections is puntstuk, act accordingly.
        # Extract sections from dict
        section_ids = list(adjacent_sections.keys())
        section_a_id = section_ids[0]
        section_b_id = section_ids[1]
        section_a_info = adjacent_sections[section_a_id]
        section_b_info = adjacent_sections[section_b_id]

        first_is_continuous, second_is_continuous = self.determine_continuous_section(section_a_info, section_b_info)

        if first_is_continuous:
            return section_a_id, section_b_id
        elif second_is_continuous:
            return section_b_id, section_a_id

        # If neither other section had puntstuk, return the one section with same hectoletter
        connected = [index for index, section in adjacent_sections.items() if
                     section_info.pos_eigs.hectoletter == section.pos_eigs.hectoletter]
        diverging = [index for index, section in adjacent_sections.items() if
                     section_info.pos_eigs.hectoletter != section.pos_eigs.hectoletter]

        if len(connected) == 1:
            return connected[0], diverging[0]

        # This connection must be an intersection, which will be treated as an end point.
        return None, None

    @staticmethod
    def __get_difference(props1: dict, props2: dict) -> dict:
        """
        Finds the key-value pairs from the first argument that do not occur in the second argument.
        Args:
            props1 (dict): First lane composition dictionary.
            props2 (dict): Second lane composition dictionary.
        Returns:
            Dictionary with all key-value pairs from the first argument that do not occur in the second argument.
        """
        return {lane_nr: lane_type for lane_nr, lane_type in props1.items()
                if (lane_nr not in props2) or (lane_nr in props2 and props2[lane_nr] != lane_type)}

    def __get_local_angle(self, overlapping_ids: list, point_geom: Point) -> float:
        """
        Find the approximate local angle of sections in the road model at a given point.
        Args:
            overlapping_ids (list): IDs of sections overlapping in the Point.
            point_geom (Point): Point for which the local angle should be obtained.
        Returns:
            Local angle in degrees.
        """
        overlapping_lines = [line for index, line in self.sections.items() if index in overlapping_ids]

        angles = []
        for line in overlapping_lines:
            # TODO: speed up using shapely.boundary()
            line_points = [point for point in line.pos_eigs.geometrie.coords]
            closest_point = min(line_points, key=lambda coord: distance(point_geom, Point(coord)))
            closest_index = line_points.index(closest_point)

            if closest_index + 1 < len(line_points):
                next_point = line_points[closest_index + 1]
            else:
                next_point = line_points[closest_index]  # Middle point

            if closest_index - 1 >= 0:
                previous_point = line_points[closest_index - 1]
            else:
                previous_point = line_points[closest_index]  # Middle point

            if next_point == previous_point:
                logger.warning(f"Geen lokale hoek gevonden voor {line}")
                continue

            delta_x = next_point[0] - previous_point[0]
            delta_y = next_point[1] - previous_point[1]

            angle_rad = math.atan2(delta_y, delta_x)
            angle_deg = math.degrees(angle_rad)
            angles.append(angle_deg)

        if not angles:
            logger.warning(f"Er iets misgegaan bij het bepalen van de lokale hoek. 0.0 wordt toegepast.")
            return 0.0

        # Drop the outlier angle from the list in case there are three (or more)
        if len(angles) > 2:
            median_angle = sorted(angles)[1]
            differences = [abs(angle - median_angle) for angle in angles]
            outlier_index = differences.index(max(differences))
            if max(differences) > 10:
                angles.pop(outlier_index)

        average_angle = sum(angles) / len(angles)
        return round(average_angle, 2)

    def determine_continuous_section(self, section1: ObjectInfo, section2: ObjectInfo) -> tuple[bool, bool]:
        """
        Given two sections, determines which section is continuous and which one diverges.
        Args:
            section1 (ObjectInfo): First section to consider.
            section2 (ObjectInfo): Second section to consider.
        Returns:
            Boolean values indicating whether the first and second provided sections are continuous.
        """
        section1_min_lane_nr, section1_max_lane_nr = self.__get_min_max_lane_number(section1.obj_eigs)
        section2_min_lane_nr, section2_max_lane_nr = self.__get_min_max_lane_number(section2.obj_eigs)

        continuous1 = (section1.obj_eigs[section1_max_lane_nr] == "Puntstuk" or
                       section2.obj_eigs[section2_min_lane_nr] == "Puntstuk")
        continuous2 = (section2.obj_eigs[section2_max_lane_nr] == "Puntstuk" or
                       section1.obj_eigs[section1_min_lane_nr] == "Puntstuk")

        return continuous1, continuous2

    def get_lane_numbers(self, obj_eigs: dict) -> tuple[list, list]:
        """
        Obtains the lane numbers, given road properties.
        Args:
            obj_eigs (dict): Road properties to be evaluated.
        Returns:
            1) The main lane numbers.
            2) The lane numbers, exluding "puntstuk" registrations.
        """
        main_lane_numbers = [lane_nr for lane_nr, lane_type in obj_eigs.items()
                             if isinstance(lane_nr, int) and lane_type in self.__MAIN_LANE_TYPES]
        drivable_lane_numbers = [lane_nr for lane_nr, lane_type in obj_eigs.items()
                                 if isinstance(lane_nr, int) and lane_type not in ["Puntstuk"]]
        return main_lane_numbers, drivable_lane_numbers

    def get_n_lanes(self, obj_eigs: dict) -> tuple[int, int]:
        """
        Determines the amount of lanes given road properties.
        Args:
            obj_eigs (dict): Road properties to be evaluated.
        Returns:
            1) The amount of main lanes.
            2) The amount of lanes, exluding "puntstuk" registrations.
        """
        main_lane_numbers, drivable_lane_numbers = self.get_lane_numbers(obj_eigs)
        return len(main_lane_numbers), len(drivable_lane_numbers)

    def get_points_info(self, specifier: str = None) -> list[ObjectInfo]:
        """
        Obtain a list of all point registrations in the road model.
        The type can be specified as "MSI", to return only MSI data.
        Args:
            specifier (str): Type specifier. Use "MSI" for msi-only
                data, and "*vergentie" for vergence point data.
        Returns:
            List of all point information.
        """
        if specifier == "MSI":
            return [point for point in self.__points.values() if point.obj_eigs["Type"] == "Signalering"]
        elif specifier == "*vergentie":
            return [point for point in self.__points.values() if point.obj_eigs["Type"] != "Signalering"]
        else:
            return [point for point in self.__points.values()]

    def get_section_by_bps(self, km: list, side: str, hecto: str = "") -> dict:
        """
        Finds the full properties of a road section at a specific km, roadside and hectoletter.
        Args:
            km (list): Kilometer range to retrieve the road section properties for.
            side (str): Side of the road to retrieve the road section properties for.
            hecto (str): Letter that gives further specification for connecting roads.
        Returns:
            Dict with ID and section information
        """
        sections = {}
        for section_index, section_info in self.sections.items():
            if (section_info.pos_eigs.rijrichting == side and section_info.pos_eigs.hectoletter == hecto and
                    (min(section_info.pos_eigs.km) <= km[0] <= max(section_info.pos_eigs.km) or
                     min(section_info.pos_eigs.km) <= km[1] <= max(section_info.pos_eigs.km))):
                sections[section_index] = section_info
        return sections

    def get_sections_by_point(self, point: Point) -> dict[int: dict]:
        """
        Finds sections in self.sections that overlap the given point.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            dict[int, dict]: Attributes of all road sections that are close to the specified point.
        """
        return {index: section for index, section in self.sections.items() if
                dwithin(point, section.pos_eigs.geometrie, DISTANCE_TOLERANCE)}

    def get_one_section_at_point(self, point: Point) -> ObjectInfo | None:
        """
        Returns the properties of a road section at a specific point. If there
        are multiple sections close to the point, the downstream section is returned.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            ObjectInfo: Attributes of the road section at the specified kilometer point.
        """
        overlapping_sections = []
        for section_info in self.sections.values():
            if dwithin(point, section_info.pos_eigs.geometrie, DISTANCE_TOLERANCE):
                if dwithin(point, Point(section_info.pos_eigs.geometrie.coords[0]), DISTANCE_TOLERANCE):
                    return section_info
                overlapping_sections.append(section_info)

        if len(overlapping_sections) > 1:
            logger.warning(f"Meerdere secties gevonden in de buurt van dit punt: {point}\n{overlapping_sections}")

        if overlapping_sections:
            return overlapping_sections[0]

        return None

    @staticmethod
    def find_gap(numbers: list[int]) -> int | None:
        """Finds the first missing number in a list of consecutive integers and returns it."""
        for number in numbers:
            if not number + 1 in numbers and not number == max(numbers):
                return number + 1
        return None


def determine_range_overlap(range1: list, range2: list) -> bool:
    """
    Determines whether there is overlap between two ranges.
    Args:
        range1 (list): First range with two float values.
        range2 (list): Second range with two float values.
    Returns:
        Boolean value indicating whether the ranges overlap or not.
        Touching ranges, such as [4, 7] and [7, 8], return False.
    """
    min1, max1 = min(range1), max(range1)
    min2, max2 = min(range2), max(range2)
    overlap = max(min1, min2) < min(max1, max2)
    return overlap


def same_direction(geom1: LineString, geom2: LineString) -> bool:
    """
    Determines whether two LineString geometries are in the same direction.
    The assumption is made that the lines overlap in such a way that a
    projection of one point on another line is accurate.
    Args:
        geom1: The first shapely LineString geometry.
        geom2: The second shapely LineString geometry.
    Returns:
        Boolean value that is True when the geometries are in the same direction.
    """
    if geom1.length <= geom2.length:
        small_geom = geom1
        large_geom = geom2
    else:
        small_geom = geom2
        large_geom = geom1

    line_distance_a = line_locate_point(large_geom, Point(small_geom.coords[0]), normalized=True)
    line_distance_b = line_locate_point(large_geom, Point(small_geom.coords[-1]), normalized=True)

    if line_distance_a == line_distance_b:
        logger.warning(f"De geometrie-richting kon niet worden bepaald met deze lijnafstanden: "
                       f"{line_distance_a, line_distance_b}. Dit geeft mogelijk verwerkingsfouten.")

    return line_distance_a < line_distance_b


def get_endpoints(geom: LineString) -> tuple[Point, Point]:
    if geom.boundary.geoms:
        start_point, end_point = geom.boundary.geoms
    else:  # Catch in case of a circular linestring
        start_point = Point(geom.coords[0])
        end_point = Point(geom.coords[-1])
    return start_point, end_point

