import geopandas as gpd
import pandas as pd
from shapely import *
from typing import Type
import csv
from copy import deepcopy
import math
import logging

# Initialize the logger
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] (%(levelname)s) %(name)s -> %(funcName)s: %(message)s')
logger = logging.getLogger(__name__)

# Set a higher level for external libraries such as fiona to filter out their debug messages
external_logger = logging.getLogger('fiona')
external_logger.setLevel(logging.INFO)


class PositieEigenschappen:
    def __init__(self, rijrichting: str = "", wegnummer: str = "", hectoletter: str = "",
                 km: list = None, geometrie: Point | LineString = None):
        self.rijrichting = rijrichting
        self.wegnummer = wegnummer
        self.hectoletter = hectoletter
        self.km = float() if km is None else km
        self.geometrie = geometrie

    def __repr__(self):
        return f"Rijrichting='{self.rijrichting}', Wegnummer='{self.wegnummer}', " \
               f"Hectoletter='{self.hectoletter}', Km={self.km}, Geometrie={self.geometrie}"


class LijnVerwerkingsEigenschappen:
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

    def __repr__(self):
        return (f"Vergentiepunt_start={self.vergentiepunt_start}, "
                f"Vergentiepunt_einde={self.vergentiepunt_einde}, "
                f"Sectie_stroomopwaarts={self.sectie_stroomopwaarts}, "
                f"Sectie_stroomafwaarts={self.sectie_stroomafwaarts}, "
                f"Sectie_afbuigend_stroomopwaarts={self.sectie_afbuigend_stroomopwaarts}, "
                f"Sectie_afbuigend_stroomafwaarts={self.sectie_afbuigend_stroomafwaarts}, "
                f"Start_kenmerk={self.start_kenmerk}, "
                f"Einde_kenmerk={self.einde_kenmerk}, "
                f"Aantal_stroken={self.aantal_stroken}, "
                f"Aantal_hoofdstroken={self.aantal_hoofdstroken}, "
                f"Aantal_rijstroken_links={self.aantal_rijstroken_links}, "
                f"Aantal_rijstroken_rechts={self.aantal_rijstroken_rechts}")


class PuntVerwerkingsEigenschappen:
    def __init__(self):
        self.sectie_ids = []
        self.ingaande_secties = []
        self.uitgaande_secties = []
        self.aantal_hoofdstroken = None
        self.aantal_stroken = None
        self.lokale_hoek = None

    def __repr__(self):
        return (f"Sectie_ids={self.sectie_ids}, "
                f"Ingaande_secties={self.ingaande_secties}, "
                f"Uitgaande_secties={self.uitgaande_secties}, "
                f"Aantal_hoofdstroken={self.aantal_hoofdstroken}, "
                f"Aantal_stroken={self.aantal_stroken}, "
                f"Lokale_hoek={self.lokale_hoek}")


class ObjectInfo:
    def __init__(self, pos_eigs: PositieEigenschappen = None, obj_eigs: dict = None):
        self.pos_eigs = PositieEigenschappen() if pos_eigs is None else pos_eigs
        self.obj_eigs = {} if obj_eigs is None else obj_eigs
        self.verw_eigs = None

    def __repr__(self):
        typename = "Sectie" if isinstance(self.pos_eigs.geometrie, LineString) else "Punt"
        return (f"{typename}:\n"
                f"Positie-eigenschappen:\n{self.pos_eigs}\n"
                f"Objecteigenschappen:\n{self.obj_eigs}\n"
                f"Verwerkingseigenschappen:\n{self.verw_eigs}\n")


class DataFrameLader:
    """
   A class for loading GeoDataFrames from shapefiles based on a specified location extent.

   Attributes:
       __LOCATIONS_CSV_PATH (str): The file path for the locations csv file.
       __FILE_PATHS (list): List of file paths for shapefiles to be loaded.
       data (dict): Dictionary to store GeoDataFrames for each layer.
       extent (box): The extent of the specified location.
   """

    __LOCATIONS_CSV_PATH = "data/locaties.csv"

    # List all data layer files to be loaded. Same structure as WEGGEG.
    __FILE_PATHS = [
        "data/Wegvakken/wegvakken.dbf",
        "data/Rijstroken/rijstroken.dbf",
        "data/Kantstroken/kantstroken.dbf",
        "data/Mengstroken/mengstroken.dbf",
        "data/Maximum snelheid/max_snelheden.dbf",
        "data/Convergenties/convergenties.dbf",
        "data/Divergenties/divergenties.dbf",
        "data/Rijstrooksignaleringen/strksignaleringn.dbf",
    ]

    __VERGENCE_NAME_MAPPING = {
        "U": "Uitvoeging",
        "D": "Splitsing",
        "C": "Samenvoeging",
        "I": "Invoeging"
    }

    def __init__(self, input_location: str | dict = None) -> None:
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            input_location (str or dict): The name of the location or a dict of coordinates.
        """

        self.data = {}
        self.lane_mapping_h = self.construct_lane_mapping("H")
        self.lane_mapping_t = self.construct_lane_mapping("T")

        if isinstance(input_location, str):
            coords = self.__get_coords_from_csv(input_location)
        else:
            coords = input_location

        self.extent = box(xmin=coords["west"], ymin=coords["zuid"], xmax=coords["oost"], ymax=coords["noord"])
        self.__load_dataframes()

    @staticmethod
    def construct_lane_mapping(direction: str) -> dict:
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
                            value = (i, "Rijstrookbeëindiging")
                        else:
                            value = (j, "ExtraRijstrook")
                    else:  # For direction "T"
                        if i == j:
                            value = (i, None)
                        elif i > j:
                            value = (i, "ExtraRijstrook")
                        else:
                            value = (j, "Rijstrookbeëindiging")
                    mapping[key] = value
        if direction == "H":
            mapping["1 -> 1.6"] = (1, "TaperStart")
            mapping["1.6 -> 1"] = (1, "TaperEinde")
            mapping["2 -> 1.6"] = (2, "TaperStart")
            mapping["1.6 -> 2"] = (2, "TaperEinde")
        if direction == "T":
            mapping["1 -> 1.6"] = (1, "TaperEinde")
            mapping["1.6 -> 1"] = (1, "TaperStart")
            mapping["2 -> 1.6"] = (2, "TaperEinde")
            mapping["1.6 -> 2"] = (2, "TaperStart")
        return mapping

    @staticmethod
    def __get_coords_from_csv(location: str) -> dict[str, float]:
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
            with open(DataFrameLader.__LOCATIONS_CSV_PATH, "r") as file:
                csv_reader = csv.DictReader(file, delimiter=";")
                for row in csv_reader:
                    if row["locatie"] == location:
                        return {
                            "noord": float(row["noord"]),
                            "oost": float(row["oost"]),
                            "zuid": float(row["zuid"]),
                            "west": float(row["west"]),
                        }
            raise ValueError(f"Ongeldige locatie: {location}. Voer een geldige naam van een locatie in.")
        except FileNotFoundError:
            raise FileNotFoundError(f"Bestand niet gevonden: {DataFrameLader.__LOCATIONS_CSV_PATH}")
        except csv.Error as e:
            raise ValueError(f"Fout bij het lezen van het csv bestand: {e}")

    def __load_dataframes(self) -> None:
        """
        Load GeoDataFrames for each layer based on the specified location.
        """
        for file_path in DataFrameLader.__FILE_PATHS:
            df_layer_name = self.__get_layer_name(file_path)
            logger.info(f"Laag {df_layer_name} laden...")
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

    @staticmethod
    def __convert_to_linestring(geom: MultiLineString) -> MultiLineString | LineString:
        """
        Deze functie is nog in aanbouw. De bedoeling is om hier MultiLineString registraties af te vangen.
        TODO 26: Fix for verbindingsboog Zonzeel.
        """
        merged = line_merge(geom)
        if isinstance(merged, LineString):
            return merged

        # Catching a specific case where there is a slight mismatch in the endpoints of a multilinestring
        if get_num_geometries(geom) == 2:
            line1 = geom.geoms[0]
            line1_points = [line1.coords[0], line1.coords[1], line1.coords[-2], line1.coords[-1]]

            line2 = geom.geoms[1]
            line2_points = [line2.coords[0], line2.coords[1], line2.coords[-2], line2.coords[-1]]

            common_points = [point for point in line1_points if point in line2_points]
            if len(common_points) == 0:
                logger.warning(f"Onverbonden MultiLineString wordt overgeslagen: {line1} en {line2}")
                return geom

            assert not len(common_points) > 1, f"Meer dan één punt gemeen tussen {line1} en {line2}: {common_points}"

            common_point = common_points[0]
            index_line1 = line1_points.index(common_point)
            index_line2 = line2_points.index(common_point)

            if index_line1 == 1:
                line1 = LineString([coord for coord in line1.coords if coord != line1_points[0]])
            if index_line1 == 2:
                line1 = LineString([coord for coord in line1.coords if coord != line1_points[-1]])
            if index_line2 == 1:
                line2 = LineString([coord for coord in line2.coords if coord != line2_points[0]])
            if index_line2 == 2:
                line2 = LineString([coord for coord in line2.coords if coord != line2_points[-1]])

            return line_merge(MultiLineString([line1, line2]))

        logger.warning(f"Omzetting naar LineString niet mogelijk voor {geom}")
        return geom

    def __edit_columns(self, name: str) -> None:
        """
        Edits columns of GeoDataFrames in self.data in place.
        Args:
            name (str): The name of the GeoDataFrame.
        """
        df = self.data[name]

        # Try to convert any MultiLineStrings to LineStrings.
        df["geometry"] = df["geometry"].apply(lambda geom: self.__convert_to_linestring(geom)
                                              if isinstance(geom, MultiLineString) else geom)

        s1 = len(df)

        # Filter so only entries are imported where the geometry column contains a LineString or Point
        df = df[df["geometry"].apply(lambda x: isinstance(x, (LineString, Point)))]

        s2 = len(df)

        if s1 - s2 > 0:
            logger.debug(f"Aantal registraties verwijderd: {s1 - s2}")

        df.loc[:, "WEGNUMMER"] = pd.to_numeric(df["WEGNUMMER"], errors="coerce").astype("Int64")

        if name == "Rijstroken":
            df["VOLGNRSTRK"] = pd.to_numeric(df["VOLGNRSTRK"], errors="raise").astype("Int64")
            df["LANE_INFO"] = df.apply(self.get_lane_info, args=("OMSCHR",), axis=1)

        if name == "Mengstroken":
            df["LANE_INFO"] = df.apply(self.get_lane_info, args=("AANT_MSK",), axis=1)

        if name == "Kantstroken":
            # "Redresseerstrook", "Bushalte", "Pechhaven" and such are not considered.
            df = df[df["OMSCHR"].isin(["Vluchtstrook", "Puntstuk", "Spitsstrook", "Plusstrook"])]

        if name == "Rijstrooksignaleringen":
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            df = df[df["CODE"] == "KP"]
            df["Type"] = "Signalering"

        # Some registrations don't have BEGINKM. These can be ignored.
        if name == "Wegvakken":
            df = df.dropna(subset=["BEGINKM"])

        if name == "Convergenties":
            df["Type"] = df["TYPE_CONV"].apply(lambda entry: self.__VERGENCE_NAME_MAPPING[entry])

        if name == "Divergenties":
            df["Type"] = df["TYPE_DIV"].apply(lambda entry: self.__VERGENCE_NAME_MAPPING[entry])

        if "stroken" in name:
            # All "stroken" dataframes have VNRWOL columns which should be converted to integer.
            df["VNRWOL"] = pd.to_numeric(df["VNRWOL"], errors="coerce").astype("Int64")

        # Assign dataframe back to original position
        self.data[name] = df

    def get_lane_info(self, row, column):
        if row["KANTCODE"] == "H":
            return self.lane_mapping_h.get(row[column], (0, None))
        else:
            return self.lane_mapping_t.get(row[column], (0, None))


class WegModel:
    __LAYER_NAMES = ["Wegvakken", "Rijstroken",
                     "Kantstroken", "Mengstroken", "Maximum snelheid",
                     "Rijstrooksignaleringen", "Convergenties", "Divergenties"]

    def __init__(self, dfl: DataFrameLader):
        self.DISTANCE_TOLERANCE = 0.3  # [m] Tolerantie-afstand voor overlap tussen punt- en lijngeometrieën.
        self.GRID_SIZE = 0.00001

        self.dfl = dfl
        self.__reference = {}
        self.__reference_index = 0
        self.sections = {}
        self.__section_index = 0
        self.points = {}
        self.__point_index = 0
        self.__has_reference_layer = False
        self.__has_initial_layer = False

        self.__import_dataframes()
        self.__post_processing()

    def __import_dataframes(self) -> None:
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
        for df_name in self.__LAYER_NAMES:
            logger.info(f"Laag '{df_name}' wordt geïmporteerd...")
            self.__import_dataframe(df_name)

    def __import_dataframe(self, df_name: str):
        """
        Load line and point features and their attributes from a GeoDataFrame.
        Args:
            df_name (str): Name of DataFrame to be imported.
        """
        dataframe = self.dfl.data[df_name]
        for index, row in dataframe.iterrows():
            feature_info = self.__extract_row_properties(row, df_name)

            if not self.__has_reference_layer:
                self.__add_reference(feature_info)
                continue

            if not self.__has_initial_layer:
                self.__add_initial_section(feature_info)
                continue

            if isinstance(row["geometry"], (Point, MultiPoint)):
                self.__add_point(feature_info)
            else:
                self.__determine_sectioning(feature_info)

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
        assert isinstance(row["geometry"], Point), f"Dit is geen simpele puntgeometrie: {row}"

        point_info = ObjectInfo()

        section_info = self.get_one_section_at_point(row["geometry"])
        point_info.pos_eigs.rijrichting = section_info.pos_eigs.rijrichting
        point_info.pos_eigs.wegnummer = section_info.pos_eigs.wegnummer
        point_info.pos_eigs.hectoletter = section_info.pos_eigs.hectoletter

        point_info.pos_eigs.km = row["KMTR"]
        point_info.pos_eigs.geometrie = row["geometry"]
        point_info.obj_eigs["Type"] = row["Type"]

        if name == "Rijstrooksignaleringen":
            point_info.obj_eigs["Rijstrooknummers"] = [int(char) for char in row["RIJSTRKNRS"]]

        return point_info

    def __extract_line_properties(self, row: pd.Series, name: str) -> ObjectInfo:
        """
        Determines line info based on a row in the dataframe
        Args:
            row (Series): Dataframe row contents
            name (str): Dataframe name
        Returns:
            Line info in generalised dict format.
        """
        assert isinstance(row["geometry"], LineString), f"Dit is geen simpele puntgeometrie: {row}"
        
        section_info = ObjectInfo()
        
        section_info.pos_eigs.km = [row["BEGINKM"], row["EINDKM"]]
        section_info.pos_eigs.geometrie = set_precision(row["geometry"], self.GRID_SIZE)

        if name == "Wegvakken":
            section_info.pos_eigs.wegnummer = row["WEGNR_HMP"]
            if row["HECTO_LTTR"]:
                section_info.pos_eigs.hectoletter = row["HECTO_LTTR"]

        elif name == "Rijstroken":
            section_info.pos_eigs.rijrichting = row["IZI_SIDE"]

            # Flip range only if travel_direction is L.
            if section_info.pos_eigs.rijrichting == "L":
                section_info.pos_eigs.km = [row["EINDKM"], row["BEGINKM"]]

            first_lane_number = row["VNRWOL"]
            n_lanes, special = row["LANE_INFO"]

            # Indicate lane number and type of lane. Example: {1: "Rijstrook", 2: "Rijstrook"}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                section_info.obj_eigs[lane_nr] = "Rijstrook"

            # Take note of special circumstances on this feature.
            if special:
                changing_lane = row["VOLGNRSTRK"]
                section_info.obj_eigs["Special"] = (special, changing_lane)

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
                section_info.obj_eigs["Special"] = special

        elif name == "Maximum snelheid":
            if math.isnan(row["BEGINTIJD"]) or row["BEGINTIJD"] == 19:
                section_info.obj_eigs["Maximumsnelheid"] = row["OMSCHR"]
            elif row["BEGINTIJD"] == 6:
                section_info.obj_eigs["Maximumsnelheid_Beperkt_Overdag"] = row["OMSCHR"]
            else:
                raise Exception(f"Deze begintijd is niet in het model verwerkt: {row['BEGINTIJD']}")

        return section_info

    def __determine_sectioning(self, new_section: ObjectInfo) -> None:
        """
        Merges the given section with existing sections in self.sections.
        Args:
            new_section (ObjectInfo): Information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            logger.warning(f"Sectie overlapt niet met eerdere lagen, dus wordt niet toegevoegd: {new_section.pos_eigs}")
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            return

        for overlapper in overlap_sections:
            if overlapper["Section_info"].pos_eigs.geometrie is None:
                # Do NOT add the section, as there was a reason the geometry is not present.
                return

        overlap_section = overlap_sections.pop(0)

        other_section_index = overlap_section["Index"]
        overlap_section_info = deepcopy(overlap_section["Section_info"])

        other_section_side = overlap_section_info.pos_eigs.rijrichting
        other_section_road_number = overlap_section_info.pos_eigs.wegnummer
        other_section_hectoletter = overlap_section_info.pos_eigs.hectoletter
        other_section_range = overlap_section_info.pos_eigs.km
        other_section_geom = overlap_section_info.pos_eigs.geometrie
        other_section_props = overlap_section_info.obj_eigs

        new_section_range = new_section.pos_eigs.km

        # Align new section range according to existing sections
        if other_section_side == "L":
            new_section_range.reverse()

        new_section_props = new_section.obj_eigs

        # Ensure all new geometries are also oriented in driving direction
        if same_direction(other_section_geom, new_section.pos_eigs.geometrie):
            new_section_geom = new_section.pos_eigs.geometrie
        else:
            new_section_geom = reverse(new_section.pos_eigs.geometrie)

        sections_to_remove = set()

        while True:

            if not self.get_overlap(new_section_geom, other_section_geom):
                if not overlap_sections:
                    break

                overlap_section = overlap_sections.pop(0)

                other_section_index = overlap_section["Index"]
                overlap_section_info = deepcopy(overlap_section["Section_info"])

                other_section_range = overlap_section_info.pos_eigs.km
                other_section_props = overlap_section_info.obj_eigs
                other_section_geom = overlap_section_info.pos_eigs.geometrie

            assert determine_range_overlap(new_section_range, other_section_range), "Bereiken overlappen niet."
            if abs(get_km_length(new_section.pos_eigs.km) - new_section.pos_eigs.geometrie.length) > 100:
                logger.warning(f"Groot lengteverschil tussen secties: {get_km_length(new_section.pos_eigs.km)} "
                               f"en {new_section.pos_eigs.geometrie.length}")

            # TODO: Fancier implementation making use of the symmetry of the code below.

            right_side = other_section_side == "R"
            left_side = other_section_side == "L"

            new_section_first = (
                                    (min(new_section_range) < min(other_section_range) and right_side)
                                ) or (
                                    (max(new_section_range) > max(other_section_range) and left_side))

            both_sections_first = (
                                      (min(new_section_range) == min(other_section_range) and right_side)
                                  ) or (
                                      (max(new_section_range) == max(other_section_range) and left_side))

            other_section_first = (
                                      (min(new_section_range) > min(other_section_range) and right_side)
                                  ) or (
                                      (max(new_section_range) < max(other_section_range) and left_side))

            # Case A: new_section starts earlier.
            # Add section between new_section_start and other_section_start
            # with new_section properties and geometry
            if new_section_first:
                # Add section...
                if right_side:
                    km_bereik = [min(new_section_range), min(other_section_range)]
                else:
                    km_bereik = [max(new_section_range), max(other_section_range)]
                added_geom = self.get_first_remainder(new_section_geom, other_section_geom)
                self.__add_section(
                    ObjectInfo(
                        pos_eigs=PositieEigenschappen(
                            rijrichting=other_section_side,
                            wegnummer=other_section_road_number,
                            hectoletter=other_section_hectoletter,
                            km=km_bereik,
                            geometrie=added_geom),
                        obj_eigs=new_section_props)
                )
                # Trim the new_section range and geometry for next iteration.
                if right_side:
                    new_section_range = [min(other_section_range), max(new_section_range)]
                else:
                    new_section_range = [max(other_section_range), min(new_section_range)]
                new_section_geom = self.get_first_remainder(new_section_geom, added_geom)

            # Case B: start is equal.
            elif both_sections_first:

                other_ends_equal = (
                                       (max(new_section_range) == max(other_section_range) and right_side)
                                   ) or (
                                       (min(new_section_range) == min(other_section_range) and left_side))

                other_section_larger = (
                                           (max(new_section_range) < max(other_section_range) and right_side)
                                       ) or (
                                           (min(new_section_range) > min(other_section_range) and left_side))

                new_section_larger = (
                                         (max(new_section_range) > max(other_section_range) and right_side)
                                     ) or (
                                         (min(new_section_range) < min(other_section_range) and left_side))

                # Update the overlapping section properties
                if other_ends_equal:
                    if not (equals(new_section_geom, other_section_geom) or (
                            equals_exact(new_section_geom, other_section_geom, tolerance=0.1))):
                        # TODO: refine these conditions
                        logger.warning(f"Geometrieën komen niet helemaal overeen: "
                                       f"{new_section_geom} and {other_section_geom}")
                    self.__update_section(other_section_index,
                                          new_km=new_section_range,
                                          new_obj_eigs=new_section_props,
                                          new_geometrie=other_section_geom)
                    # This is the final iteration.
                    break

                # Add section between new_section_min and new_section_max
                # with both properties and overlapping geometry.
                # Update other_section range between new_section_max and other_section_max
                # with and remaining geometry.
                # Remove old other_section.
                elif other_section_larger:
                    if right_side:
                        km_bereik = [min(new_section_range), max(new_section_range)]
                    else:
                        km_bereik = [max(new_section_range), min(new_section_range)]

                    added_geom = self.get_overlap(new_section_geom, other_section_geom)
                    assert added_geom, f"Geen overlap gevonden tussen {new_section_geom} en {other_section_geom}."
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section(
                        ObjectInfo(
                            pos_eigs=PositieEigenschappen(
                                rijrichting=other_section_side,
                                wegnummer=other_section_road_number,
                                hectoletter=other_section_hectoletter,
                                km=km_bereik,
                                geometrie=added_geom),
                            obj_eigs=both_props)
                    )
                    if right_side:
                        km_remaining = [max(new_section_range), max(other_section_range)]
                    else:
                        km_remaining = [min(new_section_range), min(other_section_range)]
                    other_geom = self.get_first_remainder(other_section_geom, added_geom)
                    self.__update_section(other_section_index,
                                          new_km=km_remaining,
                                          new_geometrie=other_geom)
                    # This is the final iteration.
                    break

                elif new_section_larger:
                    # Add section with both properties
                    if right_side:
                        km_bereik = [min(new_section_range), max(other_section_range)]
                    else:
                        km_bereik = [max(new_section_range), min(other_section_range)]
                    added_geom = self.get_overlap(new_section_geom, other_section_geom)
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section(
                        ObjectInfo(
                            pos_eigs=PositieEigenschappen(
                                rijrichting=other_section_side,
                                wegnummer=other_section_road_number,
                                hectoletter=other_section_hectoletter,
                                km=km_bereik,
                                geometrie=added_geom),
                            obj_eigs=both_props)
                    )
                    # We can remove the old other_section from the road model, since it has now been completely used.
                    sections_to_remove.add(other_section_index)
                    # Trim the new_section range and geometry for another iteration.
                    if right_side:
                        new_section_range = [max(other_section_range), max(new_section_range)]
                    else:
                        new_section_range = [min(other_section_range), min(new_section_range)]
                    new_section_geom = self.get_first_remainder(new_section_geom, added_geom)
                    # Determine if there are more overlapping sections to deal with.
                    if overlap_sections:
                        continue
                    else:
                        # This is the final iteration
                        self.__add_section(
                            ObjectInfo(
                                pos_eigs=PositieEigenschappen(
                                    rijrichting=other_section_side,
                                    wegnummer=other_section_road_number,
                                    hectoletter=other_section_hectoletter,
                                    km=new_section_range,
                                    geometrie=new_section_geom),
                                obj_eigs=new_section_props)
                        )
                        break

                else:
                    raise Exception("Er is iets misgegaan met het bereik.")

            # Case C: new_section starts later.
            # Add section between other_section_start and new_section_start
            # with other_section properties and geometry.
            elif other_section_first:
                # Add section...
                if right_side:
                    km_bereik = [min(other_section_range), min(new_section_range)]
                else:
                    km_bereik = [max(other_section_range), max(new_section_range)]
                added_geom = self.get_first_remainder(other_section_geom, new_section_geom)
                self.__add_section(
                    ObjectInfo(
                        pos_eigs=PositieEigenschappen(
                            rijrichting=other_section_side,
                            wegnummer=other_section_road_number,
                            hectoletter=other_section_hectoletter,
                            km=km_bereik,
                            geometrie=added_geom),
                        obj_eigs=other_section_props)
                )
                # Trim the other_section range and geometry for next iteration.
                if right_side:
                    other_section_range = [min(new_section_range), max(other_section_range)]
                else:
                    other_section_range = [max(new_section_range), min(other_section_range)]
                other_section_geom = self.get_first_remainder(other_section_geom, added_geom)

            else:
                raise Exception("Er is iets misgegaan met het bereik.")

        self.__remove_sections(sections_to_remove)

    def get_first_remainder(self, geom1: LineString, geom2: LineString) -> LineString:
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
        assert not equals_exact(geom1, geom2,
                                tolerance=self.GRID_SIZE), f"Geometriën zijn exact aan elkaar gelijk: {geom1}"
        diff = difference(geom1, geom2, grid_size=self.GRID_SIZE)

        if isinstance(diff, LineString) and not diff.is_empty:
            return diff
        elif isinstance(diff, MultiLineString) and not diff.is_empty:
            diffs = [geom for geom in diff.geoms]
            if get_num_geometries(diff) > 2:
                logger.warning(f"Meer dan 2 geometrieën resterend. Extra geometrieën: {diffs[2:]}")
            # Return the first geometry (directional order of geom1 is maintained)
            return diffs[0]
        else:
            raise Exception(f"Kan niet verder. Lege of onjuiste overgebleven geometrie ({diff}) tussen\n"
                            f"{geom1} en \n{geom2}:\n")

    def get_overlap(self, geom1: LineString, geom2: LineString) -> LineString | None:
        """
        Finds the overlap geometry between two Shapely geometries.
        Args:
            geom1 (LineString): The first Shapely LineString.
            geom2 (LineString): The second Shapely LineString.
        Returns:
            LineString describing the overlap geometry.
            Returns None if there is no overlap geometry.
        Note:
            The function uses the `intersection` method from Shapely to
            compute the overlap between the two LineString geometries.
            If the geometries do not overlap or have only a Point of
            intersection, the function returns None.
        """
        overlap_geometry = intersection(geom1, geom2, grid_size=self.GRID_SIZE)

        if isinstance(overlap_geometry, MultiLineString) and not overlap_geometry.is_empty:
            return line_merge(overlap_geometry)
        elif isinstance(overlap_geometry, LineString) and not overlap_geometry.is_empty:
            return overlap_geometry
        else:
            return None

    def __remove_sections(self, indices: set[int]) -> None:
        """
        Removes sections at the given indices.
        Args:
            indices (set): Set of indices at which to remove sections.
        """
        for index in indices:
            logger.debug(f"Sectie {index} verwijderd.\n")
            self.sections.pop(index)

    def __remove_points(self, indices: set[int]) -> None:
        """
        Removes points at the given indices.
        Args:
            indices (set): Set of indices at which to remove points.
        """
        for index in indices:
            logger.debug(f"Punt {index} verwijderd: {self.points[index]}\n")
            self.points.pop(index)

    def __update_section(self, index: int,
                         new_km: list = None, new_obj_eigs: dict = None, new_geometrie: LineString = None) -> None:
        """
        Updates one or more properties of a section at a given index.
        Prints log of section update.
        Args:
            index (int): Index of section to be updated
            new_km (list[float]): Start and end registration kilometre.
            new_obj_eigs (dict): All properties that belong to the section.
            new_geometrie (LineString): The geometry of the section.
        Prints:
            Changed section properties.
        """
        assert any([new_km, new_obj_eigs, new_geometrie]), "Update section aangeroepen, maar er is geen update nodig."
        assert new_km and new_geometrie or not (new_km or new_geometrie), \
            "Als de geometrie wordt aangepast, moet ook het bereik worden bijgewerkt. Dit geldt ook andersom."

        if new_km:
            if abs(get_km_length(new_km) - new_geometrie.length) > 100:
                logger.warning(f"Groot lengteverschil tussen secties: {get_km_length(new_km)} "
                               f"en {new_geometrie.length}")
            self.sections[index].pos_eigs.km = new_km
        if new_obj_eigs:
            self.sections[index].obj_eigs.update(new_obj_eigs)
        if new_geometrie:
            self.sections[index].pos_eigs.geometrie = new_geometrie

        self.__log_section(index, True)

    def __add_section(self, new_section: ObjectInfo) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            - new_section_info (ObjectInfo): Information class for new section.
        Prints:
            Newly added section properties.
        """
        assert not is_empty(new_section.pos_eigs.geometrie), \
            f"Poging om een lege lijngeometrie toe te voegen: {new_section.pos_eigs.geometrie}"
        if abs(get_km_length(new_section.pos_eigs.km) - new_section.pos_eigs.geometrie.length) > 100:
            logger.warning(f"Groot lengteverschil tussen secties: {get_km_length(new_section.pos_eigs.km)} "
                           f"en {new_section.pos_eigs.geometrie.length}")

        self.sections[self.__section_index] = new_section
        self.__log_section(self.__section_index, False)
        self.__section_index += 1

    def __add_initial_section(self, section_info: ObjectInfo) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            section_info (ObjectInfo): Initial section info
        Prints:
            Newly added section properties.
        """
        reference_info = self.__get_overlapping_reference_info(section_info)

        if not reference_info:
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            logger.warning(f"Sectie overlapt niet met referentie, dus wordt niet toegevoegd: {section_info.pos_eigs}")
            return

        # Ensure the first geometries are oriented in driving direction according to the reference layer.
        if same_direction(section_info.pos_eigs.geometrie, reference_info.pos_eigs.geometrie):
            geom = section_info.pos_eigs.geometrie
        else:
            geom = reverse(section_info.pos_eigs.geometrie)

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
        Prints:
            Newly added reference feature properties.
        """
        assert not is_empty(reference_info.pos_eigs.geometrie),\
            f"Poging om een lege lijngeometrie toe te voegen: {reference_info}"

        self.__reference[self.__reference_index] = reference_info
        self.__log_reference(self.__reference_index)
        self.__reference_index += 1

    def __add_point(self, point_info: ObjectInfo) -> None:
        """
        Adds a point to the points variable and increases the index.
        Args:
            point_info (ObjectInfo): Point info to be added.
        Prints:
            Newly added point properties.
        """
        assert not is_empty(point_info.pos_eigs.geometrie),\
            f"Poging om een lege puntgeometrie toe te voegen: {point_info}"

        self.points[self.__point_index] = point_info
        self.__log_point(self.__point_index)
        self.__point_index += 1

    def __log_point(self, index: int) -> None:
        """
        Logs addition of point in self.points at given index.
        Args:
            index (int): Index of point to print info for.
        """
        logger.debug(f"Punt {index} toegevoegd: \t"
                     f"{self.points[index].pos_eigs.km:<7.3f} km \t"
                     f"{self.points[index].pos_eigs.wegnummer}\t"
                     f"{self.points[index].pos_eigs.rijrichting}\t"
                     f"{self.points[index].pos_eigs.hectoletter}\t"
                     f"{self.points[index].obj_eigs} \n"
                     f"\t\t\t\t\t\t\t{set_precision(self.points[index].pos_eigs.geometrie, 1)}")

    def __log_reference(self, index: int) -> None:
        """
        Logs addition of section in self.__reference at given index.
        Args:
            index (int): Index of section to print info for.
        """
        logger.debug(f"Referentie {index} toegevoegd:  \t"
                     f"{self.__reference[index].pos_eigs.wegnummer}\t"
                     f"{self.__reference[index].pos_eigs.hectoletter}\n"
                     f"\t\t\t\t\t\t\t\t{set_precision(self.__reference[index].pos_eigs.geometrie, 1)}")

    def __log_section(self, index: int, changed: bool = False) -> None:
        """
        Logs change or addition for section in self.sections at given index.
        Args:
            index (int): Index of section to print info for.
        """
        wording = {True: "veranderd:  ", False: "toegevoegd: "}
        logger.debug(f"Sectie {index} {wording[changed]}\t"
                     f"[{self.sections[index].pos_eigs.km[0]:<7.3f}, {self.sections[index].pos_eigs.km[1]:<7.3f}] km \t"
                     f"{self.sections[index].pos_eigs.wegnummer}\t"
                     f"{self.sections[index].pos_eigs.rijrichting}\t"
                     f"{self.sections[index].pos_eigs.hectoletter}\t"
                     f"{self.sections[index].obj_eigs} \n"
                     f"\t\t\t\t\t\t\t\t{set_precision(self.sections[index].pos_eigs.geometrie, 1)}")

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
            if self.get_overlap(section_info.pos_eigs.geometrie, reference_info.pos_eigs.geometrie):
                # Return the first one found (works fine for now).
                return reference_info
        return None

    def __get_overlapping_sections(self, section_a: ObjectInfo) -> list[dict]:
        """
        Finds all sections within self which overlap with the provided section
        and returns them in a list.
        Args:
            section_a (ObjectInfo): All data pertaining to a section.
        Returns:
            A list of overlap section data, sorted by start_km depending on
            the driving direction of one of the other sections, which is assumed
            to be representative for all other sections.
        """
        overlapping_sections = []
        for section_b_index, section_b in self.sections.items():
            # First, dismiss all sections which have a non-overlapping range,
            # which prevents the more complex get_overlap() function from being called.
            if determine_range_overlap(section_a.pos_eigs.km, section_b.pos_eigs.km):
                if self.get_overlap(section_a.pos_eigs.geometrie, section_b.pos_eigs.geometrie):
                    overlapping_sections.append({"Index": section_b_index,
                                                 "Section_info": section_b})
                    # TODO: simplify to {index: section_info}

        if overlapping_sections:
            # For the rest of the implementation, sorting in driving direction is assumed.
            # Thus, sections on the left side should be ordered from high to low ranges.
            travel_direction = overlapping_sections[0]["Section_info"].pos_eigs.rijrichting
            should_reverse = travel_direction == "L"
            overlapping_sections = sorted(overlapping_sections,
                                          key=lambda x: max(x["Section_info"].pos_eigs.km),
                                          reverse=should_reverse)

        return overlapping_sections

    def __post_processing(self) -> None:
        sections_to_remove = set()
        for section_index, section_info in self.sections.items():
            # Throw out sections that do not intersect the final frame.
            if not section_info.pos_eigs.geometrie.intersects(self.dfl.extent):
                sections_to_remove.add(section_index)
                continue

            # Throw out sections that do not have (integer) lane numbers in the keys.
            if not [key for key in section_info.obj_eigs.keys() if isinstance(key, int)]:
                sections_to_remove.add(section_index)
                continue

        self.__remove_sections(sections_to_remove)

        for section_index, section_info in self.sections.items():
            section_verw_eigs = LijnVerwerkingsEigenschappen()
            
            skip_start_check = False
            skip_end_check = False

            start_point = Point(section_info.pos_eigs.geometrie.coords[0])
            end_point = Point(section_info.pos_eigs.geometrie.coords[-1])

            for point_info in self.get_points_info("*vergentie"):
                if point_info.pos_eigs.geometrie.dwithin(start_point, self.DISTANCE_TOLERANCE):
                    section_verw_eigs.vergentiepunt_start = True
                    section_verw_eigs.start_kenmerk = {key: value for key, value in section_info.obj_eigs.items()
                                                       if value in ["Invoegstrook", "Samenvoeging", "Weefstrook"]}
                    skip_start_check = True
                if point_info.pos_eigs.geometrie.dwithin(end_point, self.DISTANCE_TOLERANCE):
                    section_verw_eigs.vergentiepunt_einde = True
                    section_verw_eigs.einde_kenmerk = {key: value for key, value in section_info.obj_eigs.items()
                                                       if value in ["Uitrijstrook", "Splitsing", "Weefstrook"]}
                    skip_end_check = True

            start_sections = self.get_sections_by_point(start_point)
            end_sections = self.get_sections_by_point(end_point)

            main_up, div_up = self.__separate_main_and_div(start_sections, section_index, section_info)
            main_down, div_down = self.__separate_main_and_div(end_sections, section_index, section_info)

            section_verw_eigs.sectie_stroomopwaarts = main_up
            section_verw_eigs.sectie_stroomafwaarts = main_down
            section_verw_eigs.sectie_afbuigend_stroomopwaarts = div_up
            section_verw_eigs.sectie_afbuigend_stroomafwaarts = div_down

            if main_up and not skip_start_check:
                section_verw_eigs.start_kenmerk = (
                    self.__get_dif_props(section_info.obj_eigs, self.sections[main_up].obj_eigs))

            if main_down and not skip_end_check:
                section_verw_eigs.einde_kenmerk = (
                    self.__get_dif_props(section_info.obj_eigs, self.sections[main_down].obj_eigs))

            stroken = [lane_nr for lane_nr, lane_type in section_info.obj_eigs.items()
                       if isinstance(lane_nr, int) and lane_type not in ["Puntstuk"]]
            hoofdstrooknummers = [lane_nr for lane_nr, lane_type in section_info.obj_eigs.items()
                                  if lane_type in ["Rijstrook", "Splitsing", "Samenvoeging", "Spitsstrook", "Plusstrook"]]
            strooknummers_links = [lane_nr for lane_nr in stroken if hoofdstrooknummers and lane_nr < min(hoofdstrooknummers)]
            strooknummers_rechts = [lane_nr for lane_nr in stroken if hoofdstrooknummers and lane_nr > max(hoofdstrooknummers)]

            section_verw_eigs.aantal_stroken = len(stroken)
            section_verw_eigs.aantal_hoofdstroken = len(hoofdstrooknummers)
            section_verw_eigs.aantal_rijstroken_links = len(strooknummers_links)
            section_verw_eigs.aantal_rijstroken_rechts = len(strooknummers_rechts)

            self.sections[section_index].verw_eigs = section_verw_eigs

        points_to_remove = set()
        for point_index, point_info in self.points.items():
            point_verw_eigs = PuntVerwerkingsEigenschappen()

            overlapping_sections = self.get_sections_by_point(point_info.pos_eigs.geometrie)
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

            self.points[point_index].verw_eigs = point_verw_eigs

        self.__remove_points(points_to_remove)

    @staticmethod
    def __separate_main_and_div(connecting_sections: dict, section_index, section_info) -> tuple:
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

        assert len(adjacent_sections) == 2, "Er moeten twee secties verbonden zijn aan een puntstuk."

        # If one of the other sections is puntstuk, act accordingly.
        # Extract sections from dict
        section_ids = list(adjacent_sections.keys())
        section_a_id = section_ids[0]
        section_b_id = section_ids[1]
        section_a_info = adjacent_sections[section_a_id]
        section_b_info = adjacent_sections[section_b_id]

        section_a_max_lane_nr = max([key for key in section_a_info.obj_eigs.keys() if isinstance(key, int)])
        section_b_max_lane_nr = max([key for key in section_b_info.obj_eigs.keys() if isinstance(key, int)])

        a_is_continuous = (section_a_info.obj_eigs[section_a_max_lane_nr] == "Puntstuk"
                           or section_b_info.obj_eigs[1] == "Puntstuk")
        b_is_continuous = (section_b_info.obj_eigs[section_b_max_lane_nr] == "Puntstuk"
                           or section_a_info.obj_eigs[1] == "Puntstuk")

        if a_is_continuous:
            return section_a_id, section_b_id
        elif b_is_continuous:
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
    def __get_dif_props(section_props: dict, other_props):
        return {lane_nr: lane_type for lane_nr, lane_type in section_props.items()
                if (lane_nr not in other_props) or (lane_nr in other_props and other_props[lane_nr] != lane_type)}

    def __get_local_angle(self, overlapping_ids, point_geom: Point) -> float:
        """
        Find the approximate local angle of sections in the road model at a given point.
        Returns:
            Local angle in degrees.
        """
        # TODO: replace overlapping_ids with the info of the overlapping sections.
        overlapping_lines = [line for index, line in self.sections.items() if index in overlapping_ids]

        assert overlapping_lines, f"Punt {point_geom} overlapt niet met lijnen in het model."

        angles = []
        for line in overlapping_lines:
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

        # Drop the outlier angle from the list in case there are three (or more?)
        if len(angles) > 2:
            median_angle = sorted(angles)[1]
            differences = [abs(angle - median_angle) for angle in angles]
            outlier_index = differences.index(max(differences))
            if max(differences) > 10:
                angles.pop(outlier_index)

        average_angle = sum(angles) / len(angles)
        return round(average_angle, 2)

    @staticmethod
    def get_n_lanes(obj_eigs: dict) -> tuple[int, int]:
        """
        Determines the number of lanes given road properties.
        Args:
            obj_eigs (dict): Road properties to be evaluated.
        Returns:
            1) The number of main lanes - only "Rijstrook", "Splitsing" and "Samenvoeging" registrations.
            2) The number of lanes, exluding "puntstuk" registrations.
        """
        main_lanes = [lane_nr for lane_nr, lane_type in obj_eigs.items() if isinstance(lane_nr, int)
                      and lane_type in ["Rijstrook", "Splitsing", "Samenvoeging"]]
        any_lanes = [lane_nr for lane_nr, lane_type in obj_eigs.items() if isinstance(lane_nr, int)
                     and lane_type not in ["Puntstuk"]]
        return len(main_lanes), len(any_lanes)

    def get_points_info(self, specifier: str = None) -> list[ObjectInfo]:
        """
        Obtain a list of all point registrations in the road model.
        The type can be specified as "MSI", to return only MSI data.
        Returns:
            List of all point information.
        """
        if specifier == "MSI":
            return [point for point in self.points.values() if point.obj_eigs["Type"] == "Signalering"]
        elif specifier == "*vergentie":
            return [point for point in self.points.values() if point.obj_eigs["Type"] != "Signalering"]
        else:
            return [point for point in self.points.values()]

    def get_section_info_by_bps(self, km: float, side: str, hectoletter: str = "") -> ObjectInfo:
        """
        Finds the full properties of a road section at a specific km, roadside and hectoletter.
        Args:
            km (float): Kilometer point to retrieve the road section properties for.
            side (str): Side of the road to retrieve the road section properties for.
            hectoletter (str): Letter that gives further specification for connecting roads.
        Returns:
            dict: Attributes of the road section at the specified kilometer point and hectoletter.
        """
        for section in self.sections.values():
            if (section.pos_eigs.rijrichting == side and
                    min(section.pos_eigs.km) <= km <= max(section.pos_eigs.km) and
                    section.pos_eigs.hectoletter == hectoletter):
                return section
        raise ReferenceError(f"Geen sectie gevonden met {km}, {side} en {hectoletter}.")

    def get_sections_by_point(self, point: Point) -> dict[int: dict]:
        """
        Finds sections in self.sections that overlap the given point.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            dict[int, dict]: Attributes of the (first) road section at the specified kilometer point.
        """
        return {index: section for index, section in self.sections.items() if dwithin(point, section.pos_eigs.geometrie, self.DISTANCE_TOLERANCE)}

    def get_one_section_at_point(self, point: Point) -> ObjectInfo:
        """
        Returns the properties of a road section at a specific point.
        Assumes that only one section is close to the point, or that if there
        are multiple sections close to the point, that their properties are the same.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            ObjectInfo: Attributes of the (first) road section at the specified kilometer point.
        """
        for section_info in self.sections.values():
            if dwithin(point, section_info.pos_eigs.geometrie, self.DISTANCE_TOLERANCE):
                return section_info
        raise ReferenceError(f"Geen sectie gevonden in de buurt van dit punt: {point}")


def get_km_length(km: list[float]) -> int:
    """
    Determines the distance (in meters) covered by a range given in km.
    The order of km1 and km2 does not matter.
    Args:
        km (list): Range list of format [km1, km2]
    Returns:
        Rounded distance in meters between km1 and km2.
    """
    return round(1000 * abs(km[1] - km[0]))


def determine_range_overlap(range1: list, range2: list) -> bool:
    """
    Determines whether there is overlap between two ranges.
    Args:
        range1 (list): First range with two float values.
        range2 (list): Second range with float values.
    Returns:
        Boolean value indicating whether the sections overlap or not.
        Touching ranges such as [4, 7] and [7, 8] return False.
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

    linedist_a = line_locate_point(large_geom, Point(small_geom.coords[0]))
    linedist_b = line_locate_point(large_geom, Point(small_geom.coords[-1]))

    if linedist_a == linedist_b:
        raise Exception(f"same_direction() kan geen richting bepalen met deze lijnafstanden: {linedist_a, linedist_b}")

    return linedist_a < linedist_b
