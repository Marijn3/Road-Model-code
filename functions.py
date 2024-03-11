import geopandas as gpd
import pandas as pd
from shapely import *
import csv
from copy import deepcopy
import math

GRID_SIZE = 0.00001
MSI_RELATION_MAX_SEARCH_DISTANCE = 3500  # [m] - Richtlijn zegt max 1200 m tussen portalen. Dit wordt overschreden.
DISTANCE_TOLERANCE = 0.5  # [m] Tolerantie-afstand voor overlap tussen geometrieën.

# Mapping from lane registration to (nLanes, Special feature)
LANE_MAPPING_H = {"1 -> 1": (1, None), "1 -> 2": (2, "ExtraRijstrook"), "2 -> 1": (2, "Rijstrookbeëindiging"),
                  "1 -> 1.6": (1, "TaperStart"), "1.6 -> 1": (1, "TaperEinde"),
                  "2 -> 1.6": (2, "TaperStart"), "1.6 -> 2": (2, "TaperEinde"),
                  "2 -> 2": (2, None), "2 -> 3": (3, "ExtraRijstrook"), "3 -> 2": (3, "Rijstrookbeëindiging"),
                  "3 -> 3": (3, None), "3 -> 4": (4, "ExtraRijstrook"), "4 -> 3": (4, "Rijstrookbeëindiging"),
                  "4 -> 4": (4, None), "4 -> 5": (5, "ExtraRijstrook"), "5 -> 4": (5, "Rijstrookbeëindiging"),
                  "5 -> 5": (5, None), "5 -> 6": (6, "ExtraRijstrook"), "6 -> 5": (6, "Rijstrookbeëindiging"),
                  "6 -> 6": (6, None),
                  "7 -> 7": (7, None)}

# All registrations with T as kantcode as marked in the opposite direction.
LANE_MAPPING_T = {"1 -> 1": (1, None), "1 -> 2": (2, "Rijstrookbeëindiging"), "2 -> 1": (2, "ExtraRijstrook"),
                  "1 -> 1.6": (1, "TaperEinde"), "1.6 -> 1": (1, "TaperStart"),
                  "2 -> 1.6": (2, "TaperEinde"), "1.6 -> 2": (2, "TaperStart"),
                  "2 -> 2": (2, None), "2 -> 3": (3, "Rijstrookbeëindiging"), "3 -> 2": (3, "ExtraRijstrook"),
                  "3 -> 3": (3, None), "3 -> 4": (4, "Rijstrookbeëindiging"), "4 -> 3": (4, "ExtraRijstrook"),
                  "4 -> 4": (4, None), "4 -> 5": (5, "Rijstrookbeëindiging"), "5 -> 4": (5, "ExtraRijstrook"),
                  "5 -> 5": (5, None), "5 -> 6": (6, "Rijstrookbeëindiging"), "6 -> 5": (6, "ExtraRijstrook"),
                  "6 -> 6": (6, None),
                  "7 -> 7": (7, None)}


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

    def __init__(self, input_location: str | dict = None) -> None:
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            input_location (str or dict): The name of the location or a dict of coordinates.
        """
        self.data = {}

        if isinstance(input_location, str):
            coords = self.__get_coords_from_csv(input_location)
        else:
            coords = input_location

        self.extent = box(xmin=coords["west"], ymin=coords["zuid"], xmax=coords["oost"], ymax=coords["noord"])
        self.__load_dataframes()

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
            print(f"[LOG:] Laag {df_layer_name} laden...")
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
        data = gpd.read_file(file_path)
        return self.__select_data_in_extent(data)

    def __select_data_in_extent(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Select data that intersects the specified extent from the GeoDataFrame.
        All data that intersects the extent is considered "in the extent".
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with only data that intersects the extent.
        """
        data["inextent"] = data["geometry"].apply(lambda geom: geom.intersects(self.extent))
        return data[data["inextent"]]

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
        TODO 26: Fix for verbindingsbogen.
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
                print(f"[WAARSCHUWING:] MultiLineString zonder gemeen punt wordt overgeslagen: {line1} en {line2}")
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

        assert False, f"Omzetting naar LineString niet mogelijk voor {geom}"

    def __edit_columns(self, name: str) -> None:
        """
        Edits columns of GeoDataFrames in self.data in place.
        Args:
            name (str): The name of the GeoDataFrame.
        """
        # Try to convert any MultiLineStrings to LineStrings.
        self.data[name]["geometry"] = self.data[name]["geometry"].apply(lambda geom: self.__convert_to_linestring(geom)
                                                                        if isinstance(geom, MultiLineString) else geom)

        s1 = len(self.data[name])

        # Filter all entries where the geometry column still contains a MultiLineString
        is_linestring_or_point = self.data[name]["geometry"].apply(lambda x: isinstance(x, (LineString, Point)))
        self.data[name] = self.data[name][is_linestring_or_point]

        s2 = len(self.data[name])

        if s1 - s2 > 0:
            print(f"[LOG:] Aantal registraties verwijderd: {s1 - s2}")

        # These column variable types should be changed.
        self.data[name]["WEGNUMMER"] = pd.to_numeric(self.data[name]["WEGNUMMER"], errors="coerce").astype("Int64")

        if name == "Rijstroken":
            self.data[name]["VOLGNRSTRK"] = pd.to_numeric(self.data[name]["VOLGNRSTRK"], errors="raise").astype("Int64")

            mapping_function = lambda row: LANE_MAPPING_H[row["OMSCHR"]] if row["KANTCODE"] == "H" \
                else LANE_MAPPING_T[row["OMSCHR"]]
            self.data[name]["laneInfo"] = self.data[name].apply(mapping_function, axis=1)

        if name == "Mengstroken":
            mapping_function = lambda row: LANE_MAPPING_H[row["AANT_MSK"]] if row["KANTCODE"] == "H" \
                else LANE_MAPPING_T[row["AANT_MSK"]]
            self.data[name]["laneInfo"] = self.data[name].apply(mapping_function, axis=1)

        if name == "Kantstroken":
            # "Redresseerstrook", "Bushalte", "Pechhaven" and such are not considered.
            is_considered = self.data[name]["OMSCHR"].isin(["Vluchtstrook", "Puntstuk", "Spitsstrook", "Plusstrook"])
            self.data[name] = self.data[name][is_considered]

        if name == "Rijstrooksignaleringen":
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            is_kp = self.data[name]["CODE"] == "KP"
            self.data[name] = self.data[name][is_kp]

        # Some registrations don't have BEGINKM. These can be ignored.
        if name == "Wegvakken":
            self.data[name] = self.data[name].dropna(subset=["BEGINKM"])

        vergence_mapping = {
            "U": "Uitvoeging",
            "D": "Splitsing",
            "C": "Samenvoeging",
            "I": "Invoeging"
        }

        if name == "Convergenties":
            self.data[name]["Type"] = self.data[name]["TYPE_CONV"].apply(lambda entry: vergence_mapping[entry])

        if name == "Divergenties":
            self.data[name]["Type"] = self.data[name]["TYPE_DIV"].apply(lambda entry: vergence_mapping[entry])

        if "stroken" in name:
            # All "stroken" dataframes have VNRWOL columns which should be converted to integer.
            self.data[name]["VNRWOL"] = pd.to_numeric(self.data[name]["VNRWOL"], errors="coerce").astype("Int64")


class WegModel:
    __LAYER_NAMES = ["Wegvakken", "Rijstroken",
                     "Kantstroken", "Mengstroken", "Maximum snelheid",
                     "Rijstrooksignaleringen", "Convergenties", "Divergenties"]

    def __init__(self, dfl: DataFrameLader):
        self.base = {}
        self.base_index = 0
        self.sections = {}
        self.section_index = 0
        self.points = {}
        self.point_index = 0
        self.has_base_layer = False
        self.has_initial_layer = False

        self.__import_dataframes(dfl)
        self.__post_processing()

    def __import_dataframes(self, dfl: DataFrameLader) -> None:
        """
        Load road attributes from all DataFrames.
        Args:
            dfl (DataFrameLader): DataFrameLoader class with all dataframes.
        Note:
            The "wegvakken" layer from the shivi subset of WEGGEG is the
            first layer to be imported because these statements hold for it:
                1) it is defined everywhere where it would be necessary.
                2) it does not have internal overlap.
                3) It is a reliable source for roadside and travel_direction.
                4) It contains the hectoletter.
        """
        for df_name in self.__LAYER_NAMES:
            print(f"[STATUS:] Laag '{df_name}' wordt geïmporteerd...")
            current_sections = self.section_index
            current_points = self.point_index

            self.__import_dataframe(dfl, df_name)

            print(f"[STATUS:] {df_name} voegde {self.section_index - current_sections} secties "
                  f"en {self.point_index - current_points} punten toe aan het model.\n"
                  f"Het model heeft nu in totaal {self.section_index} secties en {self.point_index} punten.\n")

    def __import_dataframe(self, dfl: DataFrameLader, df_name: str):
        """
        Load line and point features and their attributes from a GeoDataFrame.
        Args:
            dfl (DataFrameLader): DataFrameLoader class with all dataframes.
            df_name (str): Name of DataFrame to be imported.
        """
        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            feature_info = self.__extract_row_properties(row, df_name)

            if not self.has_base_layer:
                self.__add_base(feature_info)
                continue

            if not self.has_initial_layer:
                self.__add_initial_section(feature_info)
                continue

            if isinstance(row["geometry"], (Point, MultiPoint)):
                self.__add_point(feature_info)
            else:
                self.__determine_sectioning(feature_info)

        if df_name == "Wegvakken":
            self.has_base_layer = True
        if df_name == "Rijstroken":
            self.has_initial_layer = True

    def __extract_row_properties(self, row: pd.Series, name: str):
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

    def __extract_point_properties(self, row: pd.Series, name: str) -> dict:
        """
        Determines point info based on a row in the dataframe
        Args:
            row (Series): Dataframe row contents
            name (str): Dataframe name
        Returns:
            Point info in generalised dict format.
        """
        assert isinstance(row["geometry"], Point), f"Dit is geen simpele puntgeometrie: {row}"

        point_info = {
            "Pos_eigs": {
                "Rijrichting": "",
                "Wegnummer": "",
                "Hectoletter": "",
                "Km": [],
                "Geometrie": None
            },
            "Obj_eigs": {
                "Type": ""
            },
            "Verw_eigs": {}
        }

        section_info = self.get_one_section_info_at_point(row["geometry"])
        point_info["Pos_eigs"]["Rijrichting"] = section_info["Pos_eigs"]["Rijrichting"]
        point_info["Pos_eigs"]["Wegnummer"] = section_info["Pos_eigs"]["Wegnummer"]
        point_info["Pos_eigs"]["Hectoletter"] = section_info["Pos_eigs"]["Hectoletter"]

        point_info["Pos_eigs"]["Km"] = row["KMTR"]
        point_info["Pos_eigs"]["Geometrie"] = row["geometry"]

        if name in ["Convergenties", "Divergenties"]:
            point_info["Obj_eigs"]["Type"] = row["Type"]

        if name == "Rijstrooksignaleringen":
            point_info["Obj_eigs"]["Type"] = "Signalering"
            point_info["Obj_eigs"]["Rijstrooknummers"] = [int(char) for char in row["RIJSTRKNRS"]]

        return point_info

    @staticmethod
    def __extract_line_properties(row: pd.Series, name: str) -> dict:
        """
        Determines line info based on a row in the dataframe
        Args:
            row (Series): Dataframe row contents
            name (str): Dataframe name
        Returns:
            Line info in generalised dict format.
        """
        assert isinstance(row["geometry"], LineString), f"Dit is geen simpele puntgeometrie: {row}"

        section_info = {
            "Pos_eigs": {
                "Rijrichting": "",
                "Wegnummer": "",
                "Hectoletter": "",
                "Km_bereik": [],
                "Geometrie": None
            },
            "Obj_eigs": {},
            "Verw_eigs": {}
        }

        section_info["Pos_eigs"]["Km_bereik"] = [row["BEGINKM"], row["EINDKM"]]
        section_info["Pos_eigs"]["Geometrie"] = set_precision(row["geometry"], GRID_SIZE)

        if name == "Wegvakken":
            section_info["Pos_eigs"]["Wegnummer"] = row["WEGNR_HMP"]
            if row["HECTO_LTTR"]:
                section_info["Pos_eigs"]["Hectoletter"] = row["HECTO_LTTR"]

        elif name == "Rijstroken":
            section_info["Pos_eigs"]["Rijrichting"] = row["IZI_SIDE"]

            # Flip range only if travel_direction is L.
            if section_info["Pos_eigs"]["Rijrichting"] == "L":
                section_info["Pos_eigs"]["Km_bereik"] = [row["EINDKM"], row["BEGINKM"]]

            first_lane_number = row["VNRWOL"]
            n_lanes, special = row["laneInfo"]

            # Indicate lane number and type of lane. Example: {1: "Rijstrook", 2: "Rijstrook"}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                section_info["Obj_eigs"][lane_nr] = "Rijstrook"

            # Take note of special circumstances on this feature.
            if special:
                changing_lane = row["VOLGNRSTRK"]
                section_info["Obj_eigs"]["Special"] = (special, changing_lane)

        elif name == "Kantstroken":
            # Indicate lane number and type of kantstrook. Example: {3: "Spitsstrook"}
            lane_number = row["VNRWOL"]
            section_info["Obj_eigs"][lane_number] = row["OMSCHR"]
            if row["MAX_SNELH"]:
                section_info["Obj_eigs"]["Maximumsnelheid_Open_Spitsstrook"] = row["MAX_SNELH"]

        elif name == "Mengstroken":
            first_lane_number = row["VNRWOL"]
            n_lanes, special = row["laneInfo"]

            # Indicate lane number and type of lane. Example: {4: "Weefstrook"}
            for lane_nr in range(first_lane_number, first_lane_number + n_lanes):
                section_info["Obj_eigs"][lane_nr] = row["OMSCHR"]

            # Take note of special circumstances on this feature.
            if special:
                section_info["Obj_eigs"]["Special"] = special

        elif name == "Maximum snelheid":
            if math.isnan(row["BEGINTIJD"]) or row["BEGINTIJD"] == 19:
                section_info["Obj_eigs"]["Maximumsnelheid"] = row["OMSCHR"]
            elif row["BEGINTIJD"] == 6:
                section_info["Obj_eigs"]["Maximumsnelheid_Beperkt_Overdag"] = row["OMSCHR"]
            else:
                raise Exception(f"Deze begintijd is niet in het model verwerkt: {row['BEGINTIJD']}")

        return section_info

    def __determine_sectioning(self, new_section: dict) -> None:
        """
        Merges the given section with existing sections in self.sections.
        Args:
            new_section (dict): Information related to the new section.
        """
        overlap_sections = self.__get_overlapping_sections(new_section)

        if not overlap_sections:
            print(f"[WAARSCHUWING:] {new_section} overlapt niet met eerdere lagen. Deze sectie wordt niet toegevoegd.")
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            return

        overlap_section = overlap_sections.pop(0)

        other_section_index = overlap_section["Index"]
        overlap_section_info = deepcopy(overlap_section["Section_info"])

        other_section_side = overlap_section_info["Pos_eigs"]["Rijrichting"]
        other_section_road_number = overlap_section_info["Pos_eigs"]["Wegnummer"]
        other_section_hectoletter = overlap_section_info["Pos_eigs"]["Hectoletter"]
        other_section_range = overlap_section_info["Pos_eigs"]["Km_bereik"]
        other_section_geom = overlap_section_info["Pos_eigs"]["Geometrie"]
        other_section_props = overlap_section_info["Obj_eigs"]

        new_section_range = new_section["Pos_eigs"]["Km_bereik"]

        # Align new section range according to existing sections
        if other_section_side == "L":
            new_section_range.reverse()

        new_section_props = new_section["Obj_eigs"]

        # Ensure all new geometries are also oriented in driving direction
        if same_direction(other_section_geom, new_section["Pos_eigs"]["Geometrie"]):
            new_section_geom = new_section["Pos_eigs"]["Geometrie"]
        else:
            new_section_geom = reverse(new_section["Pos_eigs"]["Geometrie"])

        sections_to_remove = set()

        while True:

            if not get_overlap(new_section_geom, other_section_geom):
                if not overlap_sections:
                    break

                overlap_section = overlap_sections.pop(0)

                other_section_index = overlap_section["Index"]
                overlap_section_info = deepcopy(overlap_section["Section_info"])

                other_section_range = overlap_section_info["Pos_eigs"]["Km_bereik"]
                other_section_props = overlap_section_info["Obj_eigs"]
                other_section_geom = overlap_section_info["Pos_eigs"]["Geometrie"]

            # print("New section range:", new_section_range)
            # print("New section props:", new_section_props)
            # print("New section geom:", set_precision(new_section["Pos_eigs"]["Geometrie"], 1))
            # print("Other section range:", other_section_range)
            # print("Other section props:", other_section_props)
            # print("Other section geom:", set_precision(other_section_geom, 1))

            assert determine_range_overlap(new_section_range, other_section_range), "Bereiken overlappen niet."
            if abs(get_km_length(new_section["Pos_eigs"]["Km_bereik"]) - new_section["Pos_eigs"]["Geometrie"].length) > 100:
                print(f"[WAARSCHUWING:] Groot lengteverschil: {get_km_length(new_section['Pos_eigs']['Km_bereik'])} "
                      f" en {new_section['Pos_eigs']['Geometrie'].length}\n")

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
                added_geom = get_first_remainder(new_section_geom, other_section_geom)
                self.__add_section({
                    "Pos_eigs": {
                        "Rijrichting": other_section_side,
                        "Wegnummer": other_section_road_number,
                        "Hectoletter": other_section_hectoletter,
                        "Km_bereik": km_bereik,
                        "Geometrie": added_geom},
                    "Obj_eigs": new_section_props,
                    "Verw_eigs": {}
                })
                # Trim the new_section range and geometry for next iteration.
                if right_side:
                    new_section_range = [min(other_section_range), max(new_section_range)]
                else:
                    new_section_range = [max(other_section_range), min(new_section_range)]
                new_section_geom = get_first_remainder(new_section_geom, added_geom)

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
                        print(f"[WAARSCHUWING:] Geometrieën komen niet helemaal overeen: "
                              f"{new_section_geom} and {other_section_geom}\n")
                    self.__update_section(other_section_index,
                                          km_bereik=new_section_range,
                                          properties=new_section_props,
                                          geometrie=other_section_geom)
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

                    added_geom = get_overlap(new_section_geom, other_section_geom)
                    assert added_geom, f"Geen overlap gevonden tussen {new_section_geom} en {other_section_geom}."
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        "Pos_eigs": {
                            "Rijrichting": other_section_side,
                            "Wegnummer": other_section_road_number,
                            "Hectoletter": other_section_hectoletter,
                            "Km_bereik": km_bereik,
                            "Geometrie": added_geom},
                        "Obj_eigs": both_props,
                        "Verw_eigs": {}
                    })
                    if right_side:
                        km_remaining = [max(new_section_range), max(other_section_range)]
                    else:
                        km_remaining = [min(new_section_range), min(other_section_range)]
                    other_geom = get_first_remainder(other_section_geom, added_geom)
                    self.__update_section(other_section_index,
                                          km_bereik=km_remaining,
                                          geometrie=other_geom)
                    # This is the final iteration.
                    break

                elif new_section_larger:
                    # Add section with both properties
                    if right_side:
                        km_bereik = [min(new_section_range), max(other_section_range)]
                    else:
                        km_bereik = [max(new_section_range), min(other_section_range)]
                    added_geom = get_overlap(new_section_geom, other_section_geom)
                    both_props = {**other_section_props, **new_section_props}
                    self.__add_section({
                        "Pos_eigs": {
                            "Rijrichting": other_section_side,
                            "Wegnummer": other_section_road_number,
                            "Hectoletter": other_section_hectoletter,
                            "Km_bereik": km_bereik,
                            "Geometrie": added_geom},
                        "Obj_eigs": both_props,
                        "Verw_eigs": {}
                    })
                    # We can remove the old other_section from the road model, since it has now been completely used.
                    sections_to_remove.add(other_section_index)
                    # Trim the new_section range and geometry for another iteration.
                    if right_side:
                        new_section_range = [max(other_section_range), max(new_section_range)]
                    else:
                        new_section_range = [min(other_section_range), min(new_section_range)]
                    new_section_geom = get_first_remainder(new_section_geom, added_geom)
                    # Determine if there are more overlapping sections to deal with.
                    if overlap_sections:
                        continue
                    else:
                        # This is the final iteration
                        self.__add_section({
                            "Pos_eigs": {
                                "Rijrichting": other_section_side,
                                "Wegnummer": other_section_road_number,
                                "Hectoletter": other_section_hectoletter,
                                "Km_bereik": new_section_range,
                                "Geometrie": new_section_geom},
                            "Obj_eigs": new_section_props,
                            "Verw_eigs": {}
                        })
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
                added_geom = get_first_remainder(other_section_geom, new_section_geom)
                self.__add_section({
                    "Pos_eigs": {
                        "Rijrichting": other_section_side,
                        "Wegnummer": other_section_road_number,
                        "Hectoletter": other_section_hectoletter,
                        "Km_bereik": km_bereik,
                        "Geometrie": added_geom},
                    "Obj_eigs": other_section_props,
                    "Verw_eigs": {}
                })
                # Trim the other_section range and geometry for next iteration.
                if right_side:
                    other_section_range = [min(new_section_range), max(other_section_range)]
                else:
                    other_section_range = [max(new_section_range), min(other_section_range)]
                other_section_geom = get_first_remainder(other_section_geom, added_geom)

            else:
                raise Exception("Er is iets misgegaan met het bereik.")

        self.__remove_sections(sections_to_remove)

    def __remove_sections(self, indices: set[int]) -> None:
        """
        Removes sections at the given indices.
        Args:
            indices (set): Set of indices at which to remove sections.
        """
        for index in indices:
            self.sections.pop(index)
            print(f"[LOG:] Sectie {index} verwijderd.\n")

    def __update_section(self, index: int, km_bereik: list = None, properties: dict = None, geometrie: LineString = None) -> None:
        """
        Updates one or more properties of a section at a given index.
        Prints log of section update.
        Args:
            index (int): Index of section to be updated
            km_bereik (list[float]): Start and end registration kilometre.
            properties (dict): All properties that belong to the section.
            geometrie (LineString): The geometry of the section.
        Prints:
            Changed section properties.
        """
        assert any([km_bereik, properties, geometrie]), "Update section aangeroepen, maar er is geen update nodig."
        assert km_bereik and geometrie or not (km_bereik or geometrie), \
            "Als de geometrie wordt aangepast, moet ook het bereik worden bijgewerkt. Dit geldt ook andersom."

        if km_bereik:
            if abs(get_km_length(km_bereik) - geometrie.length) > 100:
                print(f"[WAARSCHUWING:] Groot lengteverschil: {get_km_length(km_bereik)} en {geometrie.length}\n")
            self.sections[index]["Pos_eigs"]["Km_bereik"] = km_bereik
        if properties:
            self.sections[index]["Obj_eigs"].update(properties)
        if geometrie:
            self.sections[index]["Pos_eigs"]["Geometrie"] = geometrie

        self.__log_section(index, True)

    def __add_section(self, new_section: dict) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (dict): Containing:
                - Rijrichting (str): Side of the road. Either "R" or "L".
                - Wegnummer (str): Letter and number indicating the name of the road.
                - Km_bereik (list[float]): Start and end registration kilometre.
                - Eigenschappen (dict): All properties that belong to the section.
                - Geometrie (LineString): The geometry of the section.
        Prints:
            Newly added section properties.
        """
        assert not is_empty(new_section["Pos_eigs"]["Geometrie"]), f"Poging om een lege lijngeometrie toe te voegen: {new_section}"
        if abs(get_km_length(new_section["Pos_eigs"]["Km_bereik"]) - new_section["Pos_eigs"]["Geometrie"].length) > 100:
            print(f"[WAARSCHUWING:] Groot lengteverschil: "
                  f"{get_km_length(new_section['Pos_eigs']['Km_bereik'])} en {new_section['Pos_eigs']['Geometrie'].length}\n")

        self.sections[self.section_index] = new_section
        self.__log_section(self.section_index, False)
        self.section_index += 1

    def __add_initial_section(self, new_section: dict) -> None:
        """
        Adds a section to the sections variable and increases the index.
        Args:
            new_section (dict).
        Prints:
            Newly added section properties.
        """
        overlap_base = self.__get_overlapping_base(new_section)

        if not overlap_base:
            print(f"[WAARSCHUWING:] {new_section} overlapt niet met de basis. Deze sectie wordt niet toegevoegd.")
            # Do NOT add the section, as there is no guarantee the geometry direction is correct.
            return

        overlap_info = overlap_base["Section_info"]

        new_section["Pos_eigs"]["Wegnummer"] = overlap_info["Pos_eigs"]["Wegnummer"]
        new_section["Pos_eigs"]["Hectoletter"] = overlap_info["Pos_eigs"]["Hectoletter"]

        # Ensure the first geometries are oriented in driving direction according to the base layer.
        if not same_direction(new_section["Pos_eigs"]["Geometrie"], overlap_info["Pos_eigs"]["Geometrie"]):
            new_section["Pos_eigs"]["Geometrie"] = reverse(new_section["Pos_eigs"]["Geometrie"])

        self.__add_section(new_section)

    def __add_base(self, new_section: dict) -> None:
        """
        Adds a section to the base variable and increases the index.
        Args:
            new_section (dict): Containing at least:
                - Wegnummer (str): Letter and number indicating the name of the road.
                - Eigenschappen (dict): All properties that belong to the section.
                - Geometrie (LineString): The geometry of the section.
        Prints:
            Newly added section properties.
        """
        assert not is_empty(new_section["Pos_eigs"]["Geometrie"]), f"Poging om een lege lijngeometrie toe te voegen: {new_section}"

        self.base[self.base_index] = new_section
        self.__log_base(self.base_index)
        self.base_index += 1

    def __add_point(self, point: dict) -> None:
        """
        Adds a point to the points variable and increases the index.
        Args:
            point (dict): Containing:
                - km (float): Registration kilometre.
                - properties (dict): All properties that belong to the section.
                - geometry (Point): The geometry of the point.
        Prints:
            Newly added point properties.
        """
        assert not is_empty(point["Pos_eigs"]["Geometrie"]), f"Poging om een lege puntgeometrie toe te voegen: {point}"

        self.points[self.point_index] = point
        self.__log_point(self.point_index)
        self.point_index += 1

    def __log_point(self, index: int) -> None:
        """
        Prints addition LOG for point in self.points at given index.
        Args:
            index (int): Index of point to print info for.
        """
        print(f"[LOG:] Punt {index} toegevoegd: \t"
              f"{self.points[index]['Pos_eigs']['Km']:<7.3f} km \t"
              f"{self.points[index]['Pos_eigs']['Wegnummer']}\t"
              f"{self.points[index]['Pos_eigs']['Rijrichting']}\t"
              f"{self.points[index]['Pos_eigs']['Hectoletter']}\t"
              f"{self.points[index]['Obj_eigs']} \n"
              f"\t\t\t\t\t\t\t{set_precision(self.points[index]['Pos_eigs']['Geometrie'], 1)}")

    def __log_base(self, index: int) -> None:
        """
        Prints addition LOG for section in self.base at given index.
        Args:
            index (int): Index of section to print info for.
        """
        print(f"[LOG:] Basis {index} toegevoegd:  \t"
              f"{self.base[index]['Pos_eigs']['Wegnummer']}\t"
              f"{self.base[index]['Pos_eigs']['Hectoletter']}\n"
              f"\t\t\t\t\t\t\t\t{set_precision(self.base[index]['Pos_eigs']['Geometrie'], 1)}")

    def __log_section(self, index: int, changed: bool = False) -> None:
        """
        Prints change LOG for section in self.sections at given index.
        Args:
            index (int): Index of section to print info for.
        """
        wording = {True: "veranderd:  ", False: "toegevoegd: "}
        print(f"[LOG:] Sectie {index} {wording[changed]}\t"
              f"[{self.sections[index]['Pos_eigs']['Km_bereik'][0]:<7.3f}, {self.sections[index]['Pos_eigs']['Km_bereik'][1]:<7.3f}] km \t"
              f"{self.sections[index]['Pos_eigs']['Wegnummer']}\t"
              f"{self.sections[index]['Pos_eigs']['Rijrichting']}\t"
              f"{self.sections[index]['Pos_eigs']['Hectoletter']}\t"
              f"{self.sections[index]['Obj_eigs']} \n"
              f"\t\t\t\t\t\t\t\t{set_precision(self.sections[index]['Pos_eigs']['Geometrie'], 1)}")

    def __get_overlapping_base(self, new_section):
        overlapping_base = []
        for base_index, base in self.base.items():
            if get_overlap(new_section["Pos_eigs"]["Geometrie"], base["Pos_eigs"]["Geometrie"]):
                overlapping_base.append({"Index": base_index, "Section_info": base})

        #     # For the rest of the implementation, sorting in driving direction is assumed.
        #     # Thus, sections on the left side should be ordered from high to low ranges.
        #     travel_direction = overlapping_sections[0]["Section_info"]["Rijrichting"]
        #     should_reverse = travel_direction == "L"
        #     overlapping_sections = sorted(overlapping_sections,
        #                                   key=lambda x: max(x["Section_info"]["Km_bereik"]),
        #                                   reverse=should_reverse)
        # Return just one of them (works fine for now. TODO: make better?)
        if overlapping_base:
            return overlapping_base[0]
        return None

    def __get_overlapping_sections(self, section_a: dict) -> list[dict]:
        """
        Finds all sections within self which overlap with the provided section
        and returns them in a list.
        Args:
            section_a (dict): All data pertaining to a section.
        Returns:
            A list of overlap section data, sorted by start_km depending on
            the driving direction of one of the other sections, which is assumed
            to be representative for all other sections.
        """
        overlapping_sections = []
        for section_b_index, section_b in self.sections.items():
            # First, dismiss all sections which have a non-overlapping range,
            # which prevents the more complex get_overlap() function from being called.
            if determine_range_overlap(section_a["Pos_eigs"]["Km_bereik"], section_b["Pos_eigs"]["Km_bereik"]):
                if get_overlap(section_a["Pos_eigs"]["Geometrie"], section_b["Pos_eigs"]["Geometrie"]):
                    overlapping_sections.append({"Index": section_b_index,
                                                 "Section_info": section_b})

        if overlapping_sections:
            # For the rest of the implementation, sorting in driving direction is assumed.
            # Thus, sections on the left side should be ordered from high to low ranges.
            travel_direction = overlapping_sections[0]["Section_info"]["Pos_eigs"]["Rijrichting"]
            should_reverse = travel_direction == "L"
            overlapping_sections = sorted(overlapping_sections,
                                          key=lambda x: max(x["Section_info"]["Pos_eigs"]["Km_bereik"]),
                                          reverse=should_reverse)

        return overlapping_sections

    @staticmethod
    def get_n_lanes(prop: dict) -> tuple[int, int]:
        """
        Determines the number of lanes given road properties.
        Args:
            prop (dict): Road properties to be evaluated.
        Returns:
            1) The number of main lanes - only "Rijstrook", "Splitsing" and "Samenvoeging" registrations.
            2) The number of lanes, exluding "puntstuk" registrations.
        """
        main_lanes = [lane_nr for lane_nr, lane_type in prop.items() if isinstance(lane_nr, int)
                      and lane_type in ["Rijstrook", "Splitsing", "Samenvoeging"]]
        any_lanes = [lane_nr for lane_nr, lane_type in prop.items() if isinstance(lane_nr, int)
                     and lane_type not in ["Puntstuk"]]
        return len(main_lanes), len(any_lanes)

    def __post_processing(self) -> None:
        for section_index, section_info in self.sections.items():
            self.sections[section_index]["Verw_eigs"] = {
                "*vergentiepunt_start": None,
                "*vergentiepunt_einde": None,
                "Sectie_stroomopwaarts": None,
                "Sectie_stroomafwaarts": None,
                "Sectie_afbuigend_stroomopwaarts": None,
                "Sectie_afbuigend_stroomafwaarts": None,
                "Start_kenmerk": {},
                "Einde_kenmerk": {},
            }
            skip_start_check = False
            skip_end_check = False

            start_point = Point(section_info["Pos_eigs"]["Geometrie"].coords[0])
            end_point = Point(section_info["Pos_eigs"]["Geometrie"].coords[-1])

            for point_info in self.get_points_info("*vergentie"):
                if point_info["Pos_eigs"]["Geometrie"].dwithin(start_point, DISTANCE_TOLERANCE):
                    self.sections[section_index]["Verw_eigs"]["*vergentiepunt_start"] = True
                    self.sections[section_index]["Verw_eigs"]["Start_kenmerk"] = {
                        key: value for key, value in section_info["Obj_eigs"].items() if value in ["Invoegstrook", "Samenvoeging", "Weefstrook"]}
                    skip_start_check = True
                if point_info["Pos_eigs"]["Geometrie"].dwithin(end_point, DISTANCE_TOLERANCE):
                    self.sections[section_index]["Verw_eigs"]["*vergentiepunt_einde"] = True
                    self.sections[section_index]["Verw_eigs"]["Einde_kenmerk"] = {
                        key: value for key, value in section_info["Obj_eigs"].items() if value in ["Uitrijstrook", "Splitsing", "Weefstrook"]}
                    skip_end_check = True

            start_sections = self.get_sections_at_point(start_point)
            end_sections = self.get_sections_at_point(end_point)

            main_up, div_up = self.separate_main_and_div(start_sections, section_index, section_info)
            main_down, div_down = self.separate_main_and_div(end_sections, section_index, section_info)

            self.sections[section_index]["Verw_eigs"]["Sectie_stroomopwaarts"] = main_up
            self.sections[section_index]["Verw_eigs"]["Sectie_stroomafwaarts"] = main_down
            self.sections[section_index]["Verw_eigs"]["Sectie_afbuigend_stroomopwaarts"] = div_up
            self.sections[section_index]["Verw_eigs"]["Sectie_afbuigend_stroomafwaarts"] = div_down

            if main_up and not skip_start_check:
                self.sections[section_index]["Verw_eigs"]["Start_kenmerk"] = (
                    self.get_dif_props(section_info["Obj_eigs"], self.sections[main_up]["Obj_eigs"]))

            if main_down and not skip_end_check:
                self.sections[section_index]["Verw_eigs"]["Einde_kenmerk"] = (
                    self.get_dif_props(section_info["Obj_eigs"], self.sections[main_down]["Obj_eigs"]))

        for point_index, point_info in self.points.items():
            self.points[point_index]["Verw_eigs"] = {
                "Sectie_ids": [],
                "Ingaande_secties": [],
                "Uitgaande_secties": [],
                "Aantal_hoofdstroken": None,
                "Aantal_stroken": None,
                "Lokale_hoek": None,
            }

            overlapping_sections = self.get_sections_at_point(point_info["Pos_eigs"]["Geometrie"])
            sections_near_point = [section_id for section_id in overlapping_sections.keys()]
            self.points[point_index]["Verw_eigs"]["Sectie_ids"] = sections_near_point

            # Get the local number of (main) lanes. Take the highest value if there are multiple.
            lane_info = [self.get_n_lanes(section_info["Obj_eigs"]) for section_info in overlapping_sections.values()]
            self.points[point_index]["Verw_eigs"]["Aantal_hoofdstroken"] = max(lane_info, key=lambda x: x[0])[0]
            self.points[point_index]["Verw_eigs"]["Aantal_stroken"] = max(lane_info, key=lambda x: x[1])[1]

            self.points[point_index]["Verw_eigs"]["Lokale_hoek"] = self.get_local_angle(sections_near_point, point_info["Pos_eigs"]["Geometrie"])

            if point_info["Obj_eigs"]["Type"] in ["Samenvoeging", "Invoeging"]:
                self.points[point_index]["Verw_eigs"]["Ingaande_secties"] = [section_id for section_id, section_info in overlapping_sections.items() if self.get_n_lanes(section_info["Obj_eigs"])[1] != self.points[point_index]["Verw_eigs"]["Aantal_stroken"]]
                self.points[point_index]["Verw_eigs"]["Uitgaande_secties"] = [section_id for section_id, section_info in overlapping_sections.items() if self.get_n_lanes(section_info["Obj_eigs"])[1] == self.points[point_index]["Verw_eigs"]["Aantal_stroken"]]

            if point_info["Obj_eigs"]["Type"] in ["Splitsing", "Uitvoeging"]:
                self.points[point_index]["Verw_eigs"]["Ingaande_secties"] = [section_id for section_id, section_info in overlapping_sections.items() if self.get_n_lanes(section_info["Obj_eigs"])[1] == self.points[point_index]["Verw_eigs"]["Aantal_stroken"]]
                self.points[point_index]["Verw_eigs"]["Uitgaande_secties"] = [section_id for section_id, section_info in overlapping_sections.items() if self.get_n_lanes(section_info["Obj_eigs"])[1] != self.points[point_index]["Verw_eigs"]["Aantal_stroken"]]

    @staticmethod
    def separate_main_and_div(connecting_sections: dict, section_index, section_info) -> tuple:
        connected = [index for index in connecting_sections.keys() if index != section_index]
        if len(connected) == 0:
            return None, None

        if len(connected) == 1:
            return connected[0], None

        stream_sections = {index: section for index, section in connecting_sections.items() if index != section_index}

        # If puntstuk itself, return section with same hectoletter.
        if "Puntstuk" in section_info["Obj_eigs"].values():
            connected = [index for index, section in stream_sections.items() if
                         section_info["Pos_eigs"]["Hectoletter"] == section["Pos_eigs"]["Hectoletter"]]
            # If all hectoletters are the same, use the km registration.
            if len(connected) > 1:
                if section_info["Pos_eigs"]["Rijrichting"] == "L":
                    connected = [index for index, section in stream_sections.items() if
                                 section_info["Pos_eigs"]["Km_bereik"][1] == section["Pos_eigs"]["Km_bereik"][0]]
                if section_info["Pos_eigs"]["Rijrichting"] == "R":
                    connected = [index for index, section in stream_sections.items() if
                                 section_info["Pos_eigs"]["Km_bereik"][0] == section["Pos_eigs"]["Km_bereik"][1]]
            if len(connected) > 1:
                raise AssertionError("Meer dan één sectie lijkt kandidaat voor de hoofdbaan.")
            if len(connected) == 0:
                return None, None
            return connected[0], None

        # If one of the other sections is puntstuk, act accordingly.
        connected = [index for index, section in stream_sections.items() if "Puntstuk" in section["Obj_eigs"].values()]
        diverging = [index for index, section in stream_sections.items() if "Puntstuk" not in section["Obj_eigs"].values()]

        if len(connected) == 1:
            return connected[0], diverging[0]

        # If neither other section had puntstuk, return the one section with same hectoletter
        connected = [index for index, section in stream_sections.items() if
                     section_info["Pos_eigs"]["Hectoletter"] == section["Pos_eigs"]["Hectoletter"]]
        diverging = [index for index, section in stream_sections.items() if
                     section_info["Pos_eigs"]["Hectoletter"] != section["Pos_eigs"]["Hectoletter"]]

        if len(connected) == 1:
            return connected[0], diverging[0]

        # This connection must be an intersection, which will be treated as an end point.
        return None, None

    @staticmethod
    def get_dif_props(section_props: dict, other_props):
        return {lane_nr: lane_type for lane_nr, lane_type in section_props.items()
                if (lane_nr not in other_props) or (lane_nr in other_props and other_props[lane_nr] != lane_type)}

    def get_points_info(self, specifier: str = None) -> list[dict]:
        """
        Obtain a list of all point registrations in the road model.
        The type can be specified as "MSI", to return only MSI data.
        Returns:
            List of all point information.
        """
        if specifier == "MSI":
            return [point for point in self.points.values() if point["Obj_eigs"]["Type"] == "Signalering"]
        elif specifier == "*vergentie":
            return [point for point in self.points.values() if point["Obj_eigs"]["Type"] != "Signalering"]
        else:
            return [point for point in self.points.values()]

    def get_local_angle(self, overlapping_ids, point_geom: Point) -> float:
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
            line_points = [point for point in line["Pos_eigs"]["Geometrie"].coords]
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
                print(f"[WAARSCHUWING:] Geen lokale hoek gevonden voor {line}")
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

    def get_section_info_at(self, km: float, side: str, hectoletter: str = "") -> dict:
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
            if (section["Pos_eigs"]["Rijrichting"] == side and
                    min(section["Pos_eigs"]["Km_bereik"]) <= km <= max(section["Pos_eigs"]["Km_bereik"]) and
                    section["Pos_eigs"]["Hectoletter"] == hectoletter):
                return section
        return {}

    def get_sections_at_point(self, point: Point) -> dict[int: dict]:
        """
        Finds sections in self.sections that overlap the given point.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            dict[int, dict]: Attributes of the (first) road section at the specified kilometer point.
        """
        return {index: section for index, section in self.sections.items() if dwithin(point, section["Pos_eigs"]["Geometrie"], DISTANCE_TOLERANCE)}

    def get_one_section_info_at_point(self, point: Point) -> dict:
        """
        Returns the properties of a road section at a specific point.
        Assumes that only one section is close to the point, or that if there
        are multiple sections close to the point, that their properties are the same.
        Args:
            point (Point): Geometric position of the point.
        Returns:
            dict: Attributes of the (first) road section at the specified kilometer point.
        """
        for section_info in self.sections.values():
            if dwithin(point, section_info["Pos_eigs"]["Geometrie"], DISTANCE_TOLERANCE):
                return section_info
        return {}


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


def get_overlap(geom1: LineString, geom2: LineString) -> LineString | None:
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
    overlap_geometry = intersection(geom1, geom2, grid_size=GRID_SIZE)

    if isinstance(overlap_geometry, MultiLineString) and not overlap_geometry.is_empty:
        return line_merge(overlap_geometry)
    elif isinstance(overlap_geometry, LineString) and not overlap_geometry.is_empty:
        return overlap_geometry
    else:
        return None


def get_first_remainder(geom1: LineString, geom2: LineString) -> LineString:
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
    assert not equals_exact(geom1, geom2, tolerance=GRID_SIZE), f"Geometriën zijn exact aan elkaar gelijk: {geom1}"
    diff = difference(geom1, geom2, grid_size=GRID_SIZE)

    if isinstance(diff, LineString) and not diff.is_empty:
        return diff
    elif isinstance(diff, MultiLineString) and not diff.is_empty:
        diffs = [geom for geom in diff.geoms]
        if get_num_geometries(diff) > 2:
            print(f"[WAARSCHUWING:] Meer dan 2 geometrieën resterend. Extra geometrieën: {diffs[2:]}\n")
        # Return the first geometry (directional order of geom1 is maintained)
        return diffs[0]
    else:
        raise Exception(f"Kan niet verder. Lege of onjuiste overgebleven geometrie ({diff}) tussen\n"
                        f"{geom1} en \n{geom2}:\n")


def make_MTM_row_name(pos_eigs: dict) -> str:
    if pos_eigs["Hectoletter"]:
        return f"{pos_eigs['Wegnummer']}_{pos_eigs['Hectoletter'].upper()}:{pos_eigs['Km']}"
    else:
        return f"{pos_eigs['Wegnummer']}{pos_eigs['Rijrichting']}:{pos_eigs['Km']}"


class MSIRow:
    def __init__(self, msi_network, msi_row_info: dict, local_road_info: dict):
        self.msi_network = msi_network
        self.info = msi_row_info
        self.properties = self.info["Obj_eigs"]
        self.local_road_info = local_road_info
        self.local_road_properties = self.local_road_info["Obj_eigs"]
        self.name = make_MTM_row_name(self.info["Pos_eigs"])
        self.lane_numbers = []
        self.n_lanes = 0
        self.n_msis = 0
        self.MSIs = {}
        self.cw = {}
        self.downstream = {}
        self.upstream = {}

    def fill_row_properties(self):
        # Determine everything there is to know about the road in general
        self.lane_numbers = sorted([lane_nr for lane_nr, lane_type in self.local_road_properties.items()
                                    if isinstance(lane_nr, int) and lane_type not in ["Puntstuk"]])
        self.n_lanes = len(self.lane_numbers)
        self.n_msis = len(self.properties["Rijstrooknummers"])

        # Create all MSIs in row, passing the parent row class as argument
        self.MSIs = {msi_numbering: MSI(self, msi_numbering) for msi_numbering in self.properties["Rijstrooknummers"]}

        # Determine carriageways based on road properties
        self.cw = {}
        cw_index = 1
        lanes_in_current_cw = [1]

        for lane_number in self.lane_numbers:
            # Add final lane and stop
            if lane_number == self.n_lanes:
                last_lane = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                if last_lane:
                    self.cw[cw_index] = last_lane
                break

            current_lane = self.local_road_properties[lane_number]
            next_lane = self.local_road_properties[lane_number + 1]
            if current_lane == next_lane:
                lanes_in_current_cw.append(lane_number + 1)
            else:
                self.cw[cw_index] = [self.MSIs[i].name for i in lanes_in_current_cw if i in self.MSIs.keys()]
                lanes_in_current_cw = [lane_number + 1]
                cw_index += 1

    def determine_msi_row_relations(self):
        downstream_rows = self.msi_network.travel_roadmodel(self, True)
        for row in downstream_rows:
            for msi_row, desc in row.items():
                if msi_row is not None:
                    print("Conclusion:", msi_row.name, desc)
                    self.downstream[msi_row] = desc

        upstream_rows = self.msi_network.travel_roadmodel(self, False)
        for row in upstream_rows:
            for msi_row, desc in row.items():
                if msi_row is not None:
                    print("Conclusion:", msi_row.name, desc)
                    self.upstream[msi_row] = desc

    def fill_msi_properties(self):
        for msi in self.MSIs.values():
            msi.determine_properties()
            msi.determine_relations()
        # Separate loop to ensure all normal relations are in place before this is called.
        for msi in self.MSIs.values():
            msi.ensure_upstream_relation()


class MSINetwerk:
    def __init__(self, roadmodel: WegModel):
        self.roadmodel = roadmodel

        self.MSIrows = [MSIRow(self, msi_info, self.roadmodel.get_one_section_info_at_point(msi_info["Pos_eigs"]["Geometrie"]))
                        for row_numbering, msi_info in enumerate(self.roadmodel.get_points_info("MSI"))]

        for msi_row in self.MSIrows:
            msi_row.fill_row_properties()

        # These can only be called once all msi_rows are initialised.
        for msi_row in self.MSIrows:
            msi_row.determine_msi_row_relations()
            msi_row.fill_msi_properties()

        # Print resulting properties once everything has been determined
        for msi_row in self.MSIrows:
            for msi in msi_row.MSIs.values():
                filtered_properties = {key: value for key, value in msi.properties.items() if value is not None}
                print(f"{msi.name} heeft de volgende eigenschappen:\n{filtered_properties}")
                print("")

    def travel_roadmodel(self, msi_row: MSIRow, downstream: bool) -> list:
        """
        Initiates travel through the road model in upstream or downstream direction,
        starting from the indicated MSI row, and finds MSI rows in specified direction.
        Args:
            msi_row (MSIRow): MSIRow class object which is the starting point of the search.
            downstream: Boolean to indicate search direction. False for upstream search.
        Returns:
            List containing the first MSI rows encountered in the specified direction.
            Every MSI also has a shift and annotation value, depending on what was encountered
            during the travel towards that MSI row from the start MSI row.
        """
        starting_section_id = self.get_travel_starting_section_id(msi_row, downstream)
        current_km = msi_row.info["Pos_eigs"]["Km"]
        travel_direction = msi_row.local_road_info["Pos_eigs"]["Rijrichting"]

        print(f"Starting recursive search for {starting_section_id}, {current_km}, {downstream}, {travel_direction}")
        msis = self.find_msi_recursive(starting_section_id, current_km, downstream, travel_direction)

        if isinstance(msis, dict):
            return [msis]
        return msis

    def get_travel_starting_section_id(self, msi_row: MSIRow, downstream: bool) -> int:
        """
        Obtain section ID of section under MSI row. In case there are multiple sections,
        the upstream/downstream section will be taken as the starting section, depending
        on the indicated direction.
        Args:
            msi_row (MSIRow): MSI row instance to find section ID for.
            downstream (bool): Boolean to indicate search direction. False for upstream search.
        Returns:
            Section ID of starting section, considering the MSI row and the
            downstream/upstream search direction.
        """
        start_sections = self.roadmodel.get_sections_at_point(msi_row.info["Pos_eigs"]["Geometrie"])

        if len(start_sections) == 0:  # Nothing found
            raise Exception(f"Geen secties gevonden voor deze MSI locatie: {msi_row.info['Pos_eigs']}.")

        if len(start_sections) == 1:  # Obtain first (and only) ID in dict.
            return next(iter(start_sections.keys()))

        print("[WAARSCHUWING:] Meer dan één sectie gevonden op MSI locatie. Keuze op basis van zoekrichting.")
        if ((downstream and msi_row.local_road_info["Pos_eigs"]["Rijrichting"] == "L")
                or (not downstream and msi_row.local_road_info["Pos_eigs"]["Rijrichting"] == "R")):
            km_registration_to_equate = 1
        else:
            km_registration_to_equate = 0

        for section_id, section in start_sections.items():
            if section["Pos_eigs"]["Km_bereik"][km_registration_to_equate] == msi_row.info["Pos_eigs"]["Km"]:
                return section_id

    def find_msi_recursive(self, current_section_id: int, current_km: float, downstream: bool, travel_direction: str,
                           shift: int = 0, current_distance: float = 0, annotation: dict = None) -> list | dict:
        """
        This is recursive function, meaning that it calls itself. The function requires
        variables to keep track of where a branch of the recursive search is. These have
        to be specified, forming the starting point of the recursive search. The function
        also logs the shift, distance and annotation of that branch. The latter do not
        have to be specfied when calling the function.
        Args:
            current_section_id (int): ID of section in current iteration.
            current_km (float): Latest km registration encountered.
            downstream (bool): Value representing the search direction.
            travel_direction (str): Travel direction of traffic on the road ("L" or "R").
            shift (int): Amount of lanes shifted from the leftmost lane of the
                original road section so far.
            current_distance (float): Distance travelled through model so far. This is
                used to cut off search after passing a threshold.
            annotation (dict): Annotation so far.
        Returns:
            (List of) dictionaries, structured as: {MSIRow object: (shift, annotation)}.
            In case only one MSI row is found, the dictionary is returned directly.
            In case multiple are found, their dictionaries are placed in a list. This
            should be handled outside the function.
        """
        first_iteration = False
        if annotation is None:
            first_iteration = True
            annotation = {}

        if current_section_id is None:
            return {None: (shift, annotation)}

        current_section = self.roadmodel.sections[current_section_id]
        other_points_on_section, msis_on_section = (
            self.evaluate_section_points(current_section_id, current_km, travel_direction, downstream))

        # Base case 1: Single MSI row found.
        if len(msis_on_section) == 1:
            print(f"Single MSI row found on {current_section_id}: {msis_on_section[0]['Pos_eigs']['Km']}")
            shift, annotation = self.update_shift_annotation(shift, annotation, current_section["Verw_eigs"],
                                                             downstream, first_iteration, True)
            return {self.get_msi_row_at(msis_on_section[0]["Pos_eigs"]["Km"], msis_on_section[0]["Pos_eigs"]["Hectoletter"]): (shift, annotation)}

        # Base case 2: Multiple MSI rows found.
        if len(msis_on_section) > 1:
            nearest_msi = min(msis_on_section, key=lambda msi: abs(current_km - msi["Pos_eigs"]["Km"]))
            print(f"Multiple MSI rows found on {current_section_id}. Picking the closest one: {nearest_msi['Pos_eigs']['Km']}")
            shift, annotation = self.update_shift_annotation(shift, annotation, current_section["Verw_eigs"],
                                                             downstream, first_iteration, True)
            return {self.get_msi_row_at(nearest_msi["Pos_eigs"]["Km"], nearest_msi["Pos_eigs"]["Hectoletter"]): (shift, annotation)}

        # Base case 3: Maximum depth reached.
        current_distance += current_section["Pos_eigs"]["Geometrie"].length
        print(f"Current depth: {current_distance}")
        if current_distance >= MSI_RELATION_MAX_SEARCH_DISTANCE:
            print(f"The maximum depth was exceeded on this search: {current_distance}")
            return {None: (shift, annotation)}

        # Recursive case 1: No other points on the section.
        if not other_points_on_section:
            print(f"No other points on {current_section_id}.")
            if downstream:
                connecting_section_ids = [sid for sid in (current_section["Verw_eigs"]["Sectie_stroomafwaarts"],
                                                          current_section["Verw_eigs"]["Sectie_afbuigend_stroomafwaarts"]) if sid is not None]

            else:
                connecting_section_ids = [sid for sid in (current_section["Verw_eigs"]["Sectie_stroomopwaarts"],
                                                          current_section["Verw_eigs"]["Sectie_afbuigend_stroomopwaarts"]) if sid is not None]

            if not connecting_section_ids:
                # There are no further sections connected to the current one. Return empty-handed.
                print(f"No connections at all with {current_section_id}")
                return {None: (shift, annotation)}
            elif len(connecting_section_ids) > 1:
                # This happens in the case of intersections. These are of no interest for MSI relations.
                print(f"It seems that more than one section is connected to {current_section_id}: {connecting_section_ids}. Stopping.")
                return {None: (shift, annotation)}
            else:
                # Find an MSI row in the next section.
                next_section_id = connecting_section_ids[0]
                print(f"Looking for MSI row in the next section, {next_section_id}")
                shift, annotation = self.update_shift_annotation(shift, annotation, current_section["Verw_eigs"], downstream, first_iteration)
                return self.find_msi_recursive(connecting_section_ids[0], current_km, downstream, travel_direction,
                                               shift, current_distance, annotation)

        assert len(other_points_on_section) == 1, f"Onverwacht aantal punten op lijn: {other_points_on_section}"

        # Recursive case 2: *vergence point on the section.
        other_point = other_points_on_section[0]
        downstream_split = downstream and other_point["Obj_eigs"]["Type"] in ["Splitsing", "Uitvoeging"]
        upstream_split = not downstream and other_point["Obj_eigs"]["Type"] in ["Samenvoeging", "Invoeging"]

        if not (downstream_split or upstream_split):
            # The recursive function can be called once, for the (only) section that is in the travel direction.
            if downstream:
                next_section_id = current_section["Verw_eigs"]["Sectie_stroomafwaarts"]
                if "Puntstuk" not in current_section["Obj_eigs"].values():
                    # This is the diverging section. Determine annotation.
                    next_section = self.roadmodel.sections[next_section_id]
                    puntstuk_section_id = next_section["Verw_eigs"]["Sectie_stroomopwaarts"]
                    n_lanes_other, _ = self.roadmodel.get_n_lanes(self.roadmodel.sections[puntstuk_section_id]["Obj_eigs"])
                    shift = shift + n_lanes_other
            else:
                next_section_id = current_section["Verw_eigs"]["Sectie_stroomopwaarts"]
                if "Puntstuk" not in current_section["Obj_eigs"].values():
                    # This is the diverging section. Determine annotation.
                    next_section = self.roadmodel.sections[next_section_id]
                    puntstuk_section_id = next_section["Verw_eigs"]["Sectie_stroomafwaarts"]
                    n_lanes_other, _ = self.roadmodel.get_n_lanes(self.roadmodel.sections[puntstuk_section_id]["Obj_eigs"])
                    shift = shift + n_lanes_other

            if next_section_id:
                shift, annotation = self.update_shift_annotation(shift, annotation, current_section["Verw_eigs"], downstream, first_iteration)

            print(f"The *vergence point leads to section {next_section_id}")
            print(f"Marking {next_section_id} with +{shift}")

            return self.find_msi_recursive(next_section_id, other_point["Pos_eigs"]["Km"], downstream, travel_direction,
                                           shift, current_distance, annotation)

        if upstream_split:
            cont_section_id = current_section["Verw_eigs"]["Sectie_stroomopwaarts"]
            div_section_id = current_section["Verw_eigs"]["Sectie_afbuigend_stroomopwaarts"]
            print(f"The *vergence point is an upstream split into {cont_section_id} and {div_section_id}")
        else:
            cont_section_id = current_section["Verw_eigs"]["Sectie_stroomafwaarts"]
            div_section_id = current_section["Verw_eigs"]["Sectie_afbuigend_stroomafwaarts"]
            print(f"The *vergence point is a downstream split into {cont_section_id} and {div_section_id}")

        shift_div, _ = self.roadmodel.get_n_lanes(self.roadmodel.sections[cont_section_id]["Obj_eigs"])

        # Store negative value in this direction.
        print(f"Marking {div_section_id} with -{shift_div}")

        shift, annotation = self.update_shift_annotation(shift, annotation, current_section["Verw_eigs"], downstream, first_iteration)

        # Make it do the recursive function twice. Then return both options as a list.
        option_continuation = self.find_msi_recursive(cont_section_id, other_point["Pos_eigs"]["Km"],
                                                      downstream, travel_direction,
                                                      shift, current_distance, annotation)
        option_diversion = self.find_msi_recursive(div_section_id, other_point["Pos_eigs"]["Km"],
                                                   downstream, travel_direction,
                                                   shift - shift_div, current_distance, annotation)
        return [option_continuation, option_diversion]

    def evaluate_section_points(self, current_section_id: int, current_km: float, travel_direction: str, downstream: bool):
        # Only takes points that are upstream/downstream of current point.
        if (travel_direction == "L" and downstream) or (travel_direction == "R" and not downstream):
            other_points_on_section = [point_info for point_info in self.roadmodel.get_points_info() if
                                       current_section_id in point_info["Verw_eigs"]["Sectie_ids"] and point_info["Pos_eigs"]["Km"] < current_km]
        else:
            other_points_on_section = [point_info for point_info in self.roadmodel.get_points_info() if
                                       current_section_id in point_info["Verw_eigs"]["Sectie_ids"] and point_info["Pos_eigs"]["Km"] > current_km]

        # Further filters for MSIs specifically
        msis_on_section = [point for point in other_points_on_section if
                           point["Obj_eigs"]["Type"] == "Signalering"]

        return other_points_on_section, msis_on_section

    def update_shift_annotation(self, shift: int, annotation: dict, current_section_verw_eigs: dict, downstream: bool,
                                is_first_iteration: bool = False, is_last_iteration: bool = False) -> tuple[int, dict]:
        """
        Adapts the shift and annotation value according to the previous shift and annotation
        and the processing properties of the provided section.
        Args:
            shift (int): Shift so far.
            annotation (dict): Annotation so far.
            current_section_verw_eigs (dict): Processing properties of the section.
            downstream (bool): Indication of search direction. True => Downstream, False => Upstream .
            is_first_iteration (bool): Indicate if it is first iteration, in which case the start processing
                values of the provided section will be ignored.
            is_last_iteration (bool): Indicate if it is last iteration, in which case the end processing
                values of the provided section will be ignored.
        Returns:
            Adjusted shift and annotation.
        """
        new_annotation = self.get_annotation(current_section_verw_eigs, is_first_iteration, is_last_iteration)

        if not new_annotation:
            return shift, annotation

        lane_type = next(iter(new_annotation.values()), None)
        if downstream and lane_type == "ExtraRijstrook" or not downstream and lane_type == "Rijstrookbeeindiging":
            shift = shift + 1
        elif downstream and lane_type == "Rijstrookbeëindiging" or not downstream and lane_type == "ExtraRijstrook":
            shift = shift - 1

        # Join dicts while preventing aliasing issues.
        return shift, dict(list(annotation.items()) + list(new_annotation.items()))

    @staticmethod
    def get_annotation(section_verw_eigs: dict, start_skip: bool = False, end_skip: bool = False) -> dict:
        """
        Determines the annotation to be added to the current recursive
        search based on processing properties of the current section.
        Args:
            section_verw_eigs (dict): Processing properties of section
            start_skip (bool): Indicate whether the start values of the section should be considered.
            end_skip (bool): Indicate whether the end values of the section should be considered.
        Returns:
            Dict indicating the lane number and the annotation - the type of special case encountered.
        """
        annotation = {}

        if not start_skip:
            if "Uitrijstrook" in section_verw_eigs["Start_kenmerk"].values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs["Start_kenmerk"].items() if lane_type == "Uitrijstrook"})

            if "Samenvoeging" in section_verw_eigs["Start_kenmerk"].values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs["Start_kenmerk"].items() if lane_type == "Samenvoeging"})

            if "Weefstrook" in section_verw_eigs["Start_kenmerk"].values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs["Start_kenmerk"].items() if lane_type == "Weefstrook"})

        if not end_skip:
            if "Invoegstrook" in section_verw_eigs["Einde_kenmerk"].values():
                annotation.update({lane_nr: lane_type for lane_nr, lane_type in
                                   section_verw_eigs["Einde_kenmerk"].items() if lane_type == "Invoegstrook"})

            if "Special" in section_verw_eigs["Einde_kenmerk"].keys():
                annotation.update({value[1]: value[0] for keyword, value in
                                   section_verw_eigs["Einde_kenmerk"].items() if keyword == "Special"})

        return annotation

    def get_msi_row_at(self, km: float, hectoletter: str) -> MSIRow | None:
        """
        Find the MSI row in self.MSIrows with the provided km registration and hectoletter.
        Args:
            km (int): Point km registration to compare to.
            hectoletter (str): Point hectoletter registration to compare to.
        Returns:
            MSIRow object as specified.
        """
        for msi_row in self.MSIrows:
            if msi_row.info["Pos_eigs"]["Km"] == km and msi_row.info["Pos_eigs"]["Hectoletter"] == hectoletter:
                return msi_row
        return None


class MSILegends:
    # All possible legends.
    CROSS = 210
    RIGHT_ARROW = 209
    LEFT_ARROW = 208
    SPEED_50 = 16
    SPEED_50_FLASHERS = 15
    SPEED_50_REDRING = 14
    SPEED_70 = 13
    SPEED_70_FLASHERS = 12
    SPEED_70_REDRING = 11
    SPEED_80 = 10
    SPEED_80_FLASHERS = 9
    SPEED_80_REDRING = 8
    SPEED_90 = 7
    SPEED_90_FLASHERS = 6
    SPEED_90_REDRING = 5
    SPEED_100 = 4
    SPEED_ABOVE_100 = 3  # Blank screen
    GREEN_ARROW = 2
    END_OF_RESTRICTIONS = 1
    BLANK = 0

    # Legend set definitions
    displayset_all = {CROSS,
                      RIGHT_ARROW,
                      LEFT_ARROW,
                      SPEED_50, SPEED_50_FLASHERS, SPEED_50_REDRING,
                      SPEED_70, SPEED_70_FLASHERS, SPEED_70_REDRING,
                      SPEED_80, SPEED_80_FLASHERS, SPEED_80_REDRING,
                      SPEED_90, SPEED_90_FLASHERS, SPEED_90_REDRING,
                      SPEED_100,
                      SPEED_ABOVE_100,
                      GREEN_ARROW,
                      END_OF_RESTRICTIONS,
                      BLANK}
    displayset_leftmost = displayset_all - {LEFT_ARROW}
    displayset_rightmost = displayset_all - {RIGHT_ARROW}


class MSI(MSILegends):
    def __init__(self, parent_msi_row: MSIRow, lane_nr: int):
        self.row = parent_msi_row

        # Store all that is unique to the MSI
        self.lane_nr = lane_nr
        self.displayoptions = self.displayset_all
        self.name = f"{self.row.name}:{str(self.lane_nr)}"

        self.properties = {
            "c": None,  # Current MSI (center)
            "r": None,  # MSI right
            "l": None,  # MSI left
            "d": None,  # MSI downstream
            "ds": None,  # MSI downstream secondary
            "dt": None,  # MSI downstream taper
            "db": None,  # MSI downstream broadening (extra rijstrook)
            "dn": None,  # MSI downstream narrowing (rijstrookbeëindiging)
            "u": None,  # MSI upstream
            "us": None,  # MSI upstream secondary
            "ut": None,  # MSI upstream taper
            "ub": None,  # MSI upstream broadening (extra rijstrook)
            "un": None,  # MSI upstream narrowing (rijstrookbeëindiging)

            "STAT_V": None,  # Static maximum speed
            "DYN_V": None,  # Static maximum speed
            "C_V": None,  # True if continue-V relation
            "C_X": None,  # True if continue-X relation

            "N_row": None,  # [~] Number of MSIs in row.
            "N_TS": None,  # Number of MSIs in traffic stream.
            "N_CW": None,  # Number of MSIs in carriageway.

            "CW": None,  # All MSIs in CW.
            "CW_num": None,  # CW numbering.
            "CW_right": None,  # All MSIs in CW to the right.
            "CW_left": None,  # All MSIs in CW to the left.

            "TS": None,  # All MSIs in TS.
            "TS_num": None,  # TS numbering.
            "TS_right": None,  # All MSIs in TS to the right.
            "TS_left": None,  # All MSIs in TS to the left.

            "DIF_V_right": None,  # DIF-V influence from the right
            "DIF_V_left": None,  # DIF-V influence from the left

            "row": None,  # All MSIs in row.

            "RHL": None,  # [V] True if MSI in RHL. (Any lane that is open sometimes)
            "Exit_Entry": None,  # True if MSI in RHL and normal lanes left and right.
            "RHL_neighbor": None,  # [V] True if RHL in row.

            "Hard_shoulder_right": None,  # [V] True if hard shoulder directly to the right.
            "Hard_shoulder_left": None,  # [V] True if hard shoulder directly to the left.
        }

    def determine_properties(self):
        if "Maximumsnelheid" in self.row.local_road_properties.keys():
            self.properties["STAT_V"] = self.row.local_road_properties["Maximumsnelheid"]

        # Add DYN_V if it is applied and it is smaller than STAT_V
        dyn_v1, dyn_v2 = None, None
        if "Maximumsnelheid_Open_Spitsstrook" in self.row.local_road_properties.keys():
            dyn_v1 = self.row.local_road_properties["Maximumsnelheid_Open_Spitsstrook"]
        if "Maximumsnelheid_Beperkt_Overdag" in self.row.local_road_properties.keys():
            dyn_v2 = self.row.local_road_properties["Maximumsnelheid_Beperkt_Overdag"]
        if dyn_v1 and dyn_v2:
            self.properties["DYN_V"] = min(dyn_v1, dyn_v2)
        elif dyn_v1:
            self.properties["DYN_V"] = dyn_v1
        elif dyn_v2:
            self.properties["DYN_V"] = dyn_v2

        # TODO: Determine when C_V and C_X are true, based on road properties.
        #  This is implemented as a continue-V relation with the upstream RSU’s.
        self.properties["C_X"] = False
        self.properties["C_V"] = False

        self.properties["N_row"] = self.row.n_msis

        cw_number = None
        at_border_left = False
        at_border_right = False

        for index, msi_names in self.row.cw.items():
            if self.name in msi_names:
                cw_number = index
                at_border_left = self.name == msi_names[0]
                at_border_right = self.name == msi_names[-1]
                break

        if cw_number:
            self.properties["N_CW"] = len(self.row.cw[cw_number])
            self.properties["N_TS"] = self.properties["N_CW"]

            self.properties["CW"] = self.row.cw[cw_number]
            self.properties["CW_num"] = cw_number
            self.properties["CW_right"] = self.row.cw[cw_number + 1] if cw_number + 1 in self.row.cw.keys() else None
            self.properties["CW_left"] = self.row.cw[cw_number - 1] if cw_number - 1 in self.row.cw.keys() else None

            # Assumption: traffic stream == carriageway
            self.properties["TS"] = self.properties["CW"]
            self.properties["TS_num"] = self.properties["CW_num"]
            self.properties["TS_right"] = self.properties["CW_right"]
            self.properties["TS_left"] = self.properties["CW_left"]

            # Safest assumption: 0 for both directions.
            # Influence levels are only filled in when the MSI borders a different traffic stream.
            self.properties["DIF_V_right"] = 0 if at_border_right and cw_number + 1 in self.row.cw.keys() else None
            self.properties["DIF_V_left"] = 0 if at_border_left and cw_number - 1 in self.row.cw.keys() else None

        self.properties["row"] = [msi.name for msi in self.row.MSIs.values()]

        if self.row.local_road_properties[self.lane_nr] in ["Spitsstrook", "Plusstrook"]:
            self.properties["RHL"] = True  # TODO: Replace with RHL section name! See report Jeroen 2 p67.

        if (self.row.local_road_properties[self.lane_nr] in ["Spitsstrook", "Plusstrook"] and
                self.row.n_lanes > self.lane_nr > 1):
            self.properties["Exit_Entry"] = True

        if ("Spitsstrook" in self.row.local_road_properties.values() or
                "Plusstrook" in self.row.local_road_properties.values()):
            self.properties["RHL_neighbor"] = True

        if self.lane_nr < self.row.n_lanes and self.row.local_road_properties[self.lane_nr + 1] == "Vluchtstrook":
            self.properties["Hard_shoulder_right"] = True
        if self.lane_nr > 1 and self.row.local_road_properties[self.lane_nr - 1] == "Vluchtstrook":
            self.properties["Hard_shoulder_left"] = True

    def determine_relations(self):
        # Center and neighbors
        self.properties["c"] = self.name
        if self.lane_nr + 1 in self.row.MSIs.keys():
            self.properties["r"] = self.row.MSIs[self.lane_nr + 1].name
        if self.lane_nr - 1 in self.row.MSIs.keys():
            self.properties["l"] = self.row.MSIs[self.lane_nr - 1].name

        # Downstream relations
        for d_row, desc in self.row.downstream.items():
            shift, annotation = desc
            this_lane_projected = self.lane_nr + shift

            # Basic primary
            if this_lane_projected in d_row.MSIs.keys():
                self.properties["d"] = d_row.MSIs[this_lane_projected].name
                d_row.MSIs[this_lane_projected].properties["u"] = self.name

            if annotation:
                lane_numbers = list(annotation.keys())
                lane_types = list(annotation.values())

                # Broadening
                if (self.lane_nr in lane_numbers and annotation[self.lane_nr] == "ExtraRijstrook"
                        and this_lane_projected - 1 in d_row.MSIs.keys()):
                    print(f"Extra case with {self.lane_nr}")
                    self.properties["db"] = d_row.MSIs[this_lane_projected - 1].name
                    d_row.MSIs[this_lane_projected - 1].properties["ub"] = self.name
                # Narrowing
                if (self.lane_nr in lane_numbers and annotation[self.lane_nr] == "Rijstrookbeëindiging"
                        and this_lane_projected + 1 in d_row.MSIs.keys()):
                    print(f"Eindiging case with {self.lane_nr}")
                    self.properties["dn"] = d_row.MSIs[this_lane_projected + 1].name
                    d_row.MSIs[this_lane_projected + 1].properties["un"] = self.name

                # Secondary
                if (self.lane_nr in lane_numbers and annotation[self.lane_nr] == "Invoegstrook"
                        and this_lane_projected - 1 in d_row.MSIs.keys()):
                    print(f"Invoegstrook case with {self.lane_nr}")
                    self.make_secondary_connection(d_row.MSIs[this_lane_projected - 1], self)

                if (self.lane_nr + 1 in lane_numbers and annotation[self.lane_nr + 1] == "Uitrijstrook"
                        and this_lane_projected + 1 in d_row.MSIs.keys()):
                    print(f"Uitrijstrook case with {self.lane_nr}")
                    self.make_secondary_connection(d_row.MSIs[this_lane_projected + 1], self)

                # MSIs that encounter a samenvoeging or weefstrook downstream could have a cross relation.
                if ("Samenvoeging" in lane_types or "Weefstrook" in lane_types) and True:
                    # Relation from weefstrook/join lane to normal lane
                    if this_lane_projected in lane_numbers and annotation[this_lane_projected] in ["Samenvoeging", "Weefstrook"]:
                        if (this_lane_projected - 1 in d_row.local_road_properties.keys() and
                                d_row.local_road_properties[this_lane_projected - 1] != annotation[this_lane_projected]):
                            if this_lane_projected - 1 in d_row.MSIs.keys():
                                print(f"Cross case 1 with {self.lane_nr}")
                                self.make_secondary_connection(d_row.MSIs[this_lane_projected - 1], self)
                    # Relation from normal lane to weefstrook/join lane
                    if this_lane_projected + 1 in lane_numbers and annotation[this_lane_projected + 1] in ["Samenvoeging", "Weefstrook"]:
                        if (this_lane_projected + 1 in d_row.local_road_properties.keys() and
                                d_row.local_road_properties[this_lane_projected] != annotation[this_lane_projected + 1]):
                            if this_lane_projected + 1 in d_row.MSIs.keys():
                                print(f"Cross case 2 with {self.lane_nr}")
                                self.make_secondary_connection(d_row.MSIs[this_lane_projected + 1], self)

        # Remaining upstream primary relations
        if not self.properties["u"]:
            for u_row, desc in self.row.upstream.items():
                shift, _ = desc  # Why is annotation not used here??
                this_lane_projected = self.lane_nr + shift
                if this_lane_projected in u_row.MSIs.keys():
                    self.properties["u"] = u_row.MSIs[this_lane_projected].name

    def ensure_upstream_relation(self):
        # MSIs that do not have any upstream relation, get a secondary relation
        if (self.row.upstream and not (self.properties["u"] or self.properties["us"]
                                       or self.properties["ub"] or self.properties["un"] or self.properties["ut"])):
            print(f"[LOG:] {self.name} kan een bovenstroomse secundaire relatie gebruiken: {self.properties}")

            if True:
                print("[LOG:] Relatie wordt toegepast.")
                u_row, desc = next(iter(self.row.upstream.items()))
                print(u_row.local_road_info)
                if (u_row.local_road_info["Pos_eigs"]["Hectoletter"] ==
                        self.row.local_road_info["Pos_eigs"]["Hectoletter"]):
                    highest_msi_number = max([msi_nr for msi_nr in u_row.MSIs.keys()])
                    self.make_secondary_connection(self, u_row.MSIs[highest_msi_number])
                else:
                    # This should not occur in the Netherlands, but is here for safety.
                    print("[Waarschuwing:] Er wordt een onverwachte relatie toegevoegd.")
                    lowest_msi_number = min([msi_nr for msi_nr in u_row.MSIs.keys()])
                    self.make_secondary_connection(self, u_row.MSIs[lowest_msi_number])

    @staticmethod
    def make_secondary_connection(row1, row2):
        """
        First entry is the row that should have an upstream secondary relation to the second entry.
        """
        row1.properties["us"] = row2.name
        if not row2.properties["ds"]:
            row2.properties["ds"] = []
        if row1.name not in row2.properties["ds"]:
            row2.properties["ds"].append(row1.name)
