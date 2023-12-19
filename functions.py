import geopandas as gpd
import pandas as pd
from shapely import *
import csv

pd.set_option('display.max_columns', None)


class DataFrameLoader:
    """
   A class for loading GeoDataFrames from shapefiles based on a specified location extent.

   Attributes:
       __LOCATIONS_CSV_PATH (str): The file path for the locations csv file.
       __FILE_PATHS (list): List of file paths for shapefiles to be loaded.
       data (dict): Dictionary to store GeoDataFrames for each layer.
       extent (box): The extent of the specified location.
   """

    __LOCATIONS_CSV_PATH = 'data/locations.csv'

    # List all data layer files to be loaded.
    __FILE_PATHS = [
        "data/Rijstroken/rijstroken.dbf",
        "data/Kantstroken/kantstroken.dbf",
        # "data/Mengstroken/mengstroken.dbf",
        # "data/Maximum snelheid/max_snelheden.dbf",
        # "data/Convergenties/convergenties.dbf",
        # "data/Divergenties/divergenties.dbf",
        # "data/Rijstrooksignaleringen/strksignaleringn.dbf",
    ]

    def __init__(self):
        self.data = {}
        self.extent = None

    def load_data_frames(self, location: str):
        """
        Load GeoDataFrames for each layer based on the specified location.
        Args:
            location (str): The name of the location.
        """
        self.__get_extent(location)
        for file_path in DataFrameLoader.__FILE_PATHS:
            df_layer_name = self.__get_layer_name(file_path)
            self.data[df_layer_name] = self.__load_data_frame(file_path)
            self.__edit_columns(df_layer_name)

    def __load_data_frame(self, file_path: str) -> gpd.GeoDataFrame:
        """
        Load the extent-intersecting parts of a GeoDataFrame from a shapefile.
        Args:
            file_path (str): The path to the shapefile.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with selected data.
        """
        data = gpd.read_file(file_path)
        return self.__select_data_in_extent(data)

    def __get_extent(self, location: str) -> box:
        """
        Determine the extent box of the specified location from coordinates.
        Args:
            location (str): The name of the location.
        Raises:
            ValueError: If the specified location is not found in the csv file.
        """
        coords = self.__load_extent_from_csv(location)

        if coords:
            self.extent = box(xmin=coords["west"], ymin=coords["south"], xmax=coords["east"], ymax=coords["north"])
        else:
            raise ValueError(f"Invalid place: {location}. Please provide a valid location.")

    def __select_data_in_extent(self, data: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Select data in the specified extent from the GeoDataFrame.
        Args:
            data (gpd.GeoDataFrame): The GeoDataFrame.
        Returns:
            gpd.GeoDataFrame: The GeoDataFrame with only data inside the extent.
        """
        # All data that intersects extent is considered 'in the extent'.
        data['inextent'] = data['geometry'].apply(lambda geom: geom.intersects(self.extent))
        return data[data['inextent']]

    @staticmethod
    def __get_layer_name(file_path) -> str:
        """
        Extract the layer name from the file path.
        Args:
            file_path (str): The path to the file.
        Returns:
            str: The layer name.
        """
        # Folder name is extracted and used as the layer name.
        parts = file_path.split("/")
        folder_name = parts[-2]
        return folder_name

    def __edit_columns(self, df_name: str):
        """
        Edit columns from the GeoDataFrame.
        Args:
            df_name (str): The name of the GeoDataFrame.
        """
        data = self.data[df_name]

        # The geometry column can be rounded
        data['geometry'] = data['geometry'].apply(lambda geom: set_precision(geom, 0.01))

        # These columns are not necessary in this project.
        data.drop(columns=['FK_VELD4', 'IBN', 'inextent'], inplace=True)

        # These column variable types should be changed.
        data['WEGNUMMER'] = pd.to_numeric(data['WEGNUMMER'], errors='coerce').astype('Int64')

        # All 'stroken' dataframes have VNRWOL columns which should be converted to integer
        if 'stroken' in df_name:
            data['VNRWOL'] = pd.to_numeric(data['VNRWOL'], errors='coerce').astype('Int64')

        # More specific data edits
        if df_name == 'Rijstroken':
            lane_mapping = {'1 -> 1': 1, '2 -> 2': 2, '3 -> 3': 3, '4 -> 4': 4, '5 -> 5': 5}
            data['nLanes'] = data['OMSCHR'].apply(lambda df: lane_mapping.get(df, df))
            data.drop(columns=['OMSCHR'])

            # VOLGNRSTRK to integer, supporting NaN values
            data['VOLGNRSTRK'] = (pd.to_numeric(data['VOLGNRSTRK'], errors='coerce').astype('Int64'))

        elif df_name == 'Kantstroken':
            data['Vluchtstrook'] = data['OMSCHR'] == 'Vluchtstrook'
            data['Spitsstrook'] = data['OMSCHR'] == 'Spitsstrook'
            data['Puntstuk'] = data['OMSCHR'] == 'Puntstuk'  # TODO: Add support for more options
            data.drop(columns=['OMSCHR'])

        elif df_name == 'Rijstrooksignaleringen':
            # Select only the KP (kruis-pijl) signaling in Rijstrooksignaleringen
            data = data[data['CODE'] == 'KP']

    @staticmethod
    def __load_extent_from_csv(location: str) -> dict:
        """
        Load the extent coordinates of the specified location from the csv file.
        Args:
            location (str): The name of the location.
        Returns:
            dict: The extent coordinates (north, east, south, west).
        Raises:
            FileNotFoundError: If the file in the location of the filepath is not found.
            ValueError: If there is an error reading the csv file.
        """
        try:
            with open(DataFrameLoader.__LOCATIONS_CSV_PATH, 'r') as file:
                csv_reader = csv.DictReader(file, delimiter=';')
                for row in csv_reader:
                    if row['location'] == location:
                        return {
                            'north': float(row['north']),
                            'east': float(row['east']),
                            'south': float(row['south']),
                            'west': float(row['west']),
                        }
            return {}  # Return empty dictionary if the location is not found
        except FileNotFoundError:
            raise FileNotFoundError(f"File was not found: {DataFrameLoader.__LOCATIONS_CSV_PATH}")
        except csv.Error as e:
            raise ValueError(f"Error reading csv file: {e}")


class RoadModel:
    def __init__(self):
        self.sections = {}
        self.section_index = 0

    def import_dataframes(self, dfl: DataFrameLoader):
        """
        Load road attributes from all DataFrames.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
        """
        self.__import_dataframe(dfl, 'Rijstroken')
        self.__import_dataframe(dfl, 'Kantstroken')
        # self.__import_dataframe(dfl, 'Maximum snelheid')

    def __import_dataframe(self, dfl: DataFrameLoader, df_name: str):
        """
        Load road sections and attributes from a DataFrame.
        Args:
            dfl (DataFrameLoader): DataFrameLoader class with all dataframes.
            df_name (str): Name of dataframe to be imported.
        """
        # print('Currently importing', df_name, '...')
        if df_name == 'Rijstroken':
            columns_of_interest = ['nLanes']
        elif df_name == 'Kantstroken':
            columns_of_interest = ['Vluchtstrook', 'Spitsstrook', 'Puntstuk']
        elif df_name == 'Maximum snelheid':
            columns_of_interest = ['OMSCHR']
        else:
            columns_of_interest = []

        # TODO: First import can be made simpler, by ignoring overlap (as long as there is no inter-layer overlap)

        dataframe = dfl.data[df_name]
        for index, row in dataframe.iterrows():
            self.__determine_sectioning(row, columns_of_interest)

    def __determine_sectioning(self, row: pd.Series, columns_of_interest: list[str]):
        """
        Determine how to merge new section to existing sections.
        Args:
            row (pd.Series): A row from a dataframe.
            columns_of_interest (list[str]): list of column names to be extracted
        """
        new_section_side = row['IZI_SIDE']
        new_section_begin = row['BEGINKM']
        new_section_end = row['EINDKM']
        new_section_properties = row[columns_of_interest].to_dict()
        new_section_geometry = row['geometry']

        print("")
        print("Now adding section", self.section_index, ":", new_section_side, [new_section_begin, new_section_end],
                                                             new_section_properties, new_section_geometry)

        overlapping_sections = []
        for other_section_index, other_section in self.sections.items():
            # First, dismiss all sections which have a completely different begin and end range. THIS SAVES TIME.
            if self.__determine_range_overlap([new_section_begin, new_section_end], other_section['km_range']):

                overlap_geometry, overlap_present = self.__check_overlap(new_section_geometry, other_section['geometry'])

                if overlap_present:
                    overlapping_sections.append({'geom': overlap_geometry,
                                                 'section': other_section,
                                                 'index': other_section_index})

        if not overlapping_sections:
            # No overlap with other sections. Add section regularly
            print("This is a new section without overlap.")
            self.__add_section(new_section_side, [new_section_begin, new_section_end],
                               new_section_properties, new_section_geometry)
        else:
            # Loop over all overlap instances.
            while len(overlapping_sections) > 0:
                print("Number of overlapping sections:", len(overlapping_sections))
                # Extract relevant overlap properties of the first item and remove it from the list
                overlap_geometry = overlapping_sections[0]['geom']
                other_section = overlapping_sections[0]['section']
                other_section_index = overlapping_sections[0]['index']
                overlapping_sections.pop(0)

                other_section_side = other_section['side']
                other_section_range = other_section['km_range']
                other_section_begin = min(other_section_range)
                other_section_end = max(other_section_range)
                other_section_properties = other_section['properties']
                other_section_geometry = other_section['geometry']

                print('New section geom:', row['geometry'])
                print('Other section geom:', other_section_geometry)
                print('Overlap geom:', overlap_geometry)

                assert new_section_side == other_section_side, "The overlap is not on the same side of the road."

                # Set has only unique values
                registration_points = sorted({new_section_begin, new_section_end,
                                              other_section_begin, other_section_end})
                # print(registration_points).

                # Fully equal case, with 1 resulting section. 1 possible combination.
                # Desired behaviour:
                # - Add new_section's property to original entry.
                # - Change nothing else.
                if len(registration_points) == 2:
                    assert new_section_geometry.equals(other_section_geometry), 'Inconsistent geometries.'
                    print('Found equal geometries with equal start and end. Combining the properties...')
                    self.__update_section(other_section_index, new_section_properties)

                # 1/2 equal case, with 2 resulting sections. 4 possible combinations.
                # Desired behaviour:
                # - Add overlapping section (by updating the original other_section)
                #   - Determine start and end of section
                #   - Apply both properties
                #   - Reduce geometry size
                # - Add new section (by deriving the remainder)
                #   - Determine start and end of remainder section
                #   - Select property of remainder section
                #   - Increase index
                elif len(registration_points) == 3:
                    remaining_geometry = other_section_geometry.difference(new_section_geometry)

                    # If empty, try the other way around.
                    if is_empty(remaining_geometry):
                        remaining_geometry = new_section_geometry.difference(other_section_geometry)

                    print('Remaining geom:', remaining_geometry)

                    # Check that there is a non-empty valid remaining geometry.
                    assert get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometry.'
                    assert isinstance(remaining_geometry, LineString), 'Remaining part is not a LineString.'

                    print('Found equal geometries with equal start OR end. Determining sections...')

                    # Update other section
                    midpoint = registration_points[1]

                    if new_section_begin == other_section_begin:
                        km_range = [midpoint, new_section_begin]
                    elif new_section_end == other_section_end:
                        km_range = [midpoint, new_section_end]

                    self.__update_section(other_section_index, km_range, new_section_properties, overlap_geometry)

                    # Create new section
                    remainder_properties = {}

                    # Determine relevant registration point
                    if new_section_begin == other_section_begin:
                        used_points = [midpoint, new_section_begin]
                    elif new_section_end == other_section_end:
                        used_points = [midpoint, new_section_end]
                    remainder_rp = [point for point in registration_points if point not in used_points][0]

                    if remainder_rp == new_section_begin or new_section_end:
                        remainder_properties = new_section_properties
                    elif remainder_rp == other_section_begin or other_section_end:
                        remainder_properties = other_section_properties

                    self.__add_section(new_section_side, [remainder_rp, midpoint],
                                       remainder_properties, remaining_geometry)

                # 0/2 equal case, with 3 resulting sections. 4 possible combinations
                # Desired behaviour:
                # - Determine appropriate problem splitting
                elif len(registration_points) == 4:
                    remaining_geometry = other_section_geometry.symmetric_difference(new_section_geometry)

                    print('Remaining geom:', remaining_geometry)
                    # print(get_num_geometries(remaining_geometry))

                    # Check that there is a non-empty remaining geometry.
                    assert get_num_coordinates(remaining_geometry) != 0, 'Empty remaining geometryyy.'
                    assert isinstance(remaining_geometry, MultiLineString), 'Incorrect remaining geometry'

                    print('Found partly overlapping geometries. Determining problem splitting...')

                    # Overlapping section
                    logpoints = [new_section_begin, new_section_end, other_section_begin, other_section_end]
                    logpoints.sort()

                    self.sections[other_section_index]['km_range'] = sorted([logpoints[1], logpoints[2]])
                    self.sections[other_section_index]['properties'].update(new_section_properties)
                    self.sections[other_section_index]['geometry'] = overlap_geometry

                    print("Adjusted the properties of section", other_section_index, ":",
                          self.sections[other_section_index]['side'],
                          self.sections[other_section_index]['km_range'],
                          self.sections[other_section_index]['properties'],
                          self.sections[other_section_index]['geometry'])

                    # Add new sections
                    remaining_geometries = [geom for geom in remaining_geometry.geoms]
                    assert len(remaining_geometries) == 2, 'There are too many remaining geometries in the geom below.'
                    for i in [0, 1]:
                        remaining_properties = {}
                        _, new_overlap = self.__check_overlap(remaining_geometries[i], new_section_geometry)
                        _, other_overlap = self.__check_overlap(remaining_geometries[i], other_section_geometry)
                        print(new_overlap, other_overlap)
                        if new_overlap:
                            remainder_properties = new_section_properties
                        elif other_overlap:
                            remainder_properties = other_section_properties

                        self.__add_section(new_section_side, [logpoints[i*2], logpoints[i*2+1]],
                                           remainder_properties, remaining_geometries[i])

    @staticmethod
    def __determine_range_overlap(range1: list, range2: list) -> bool:
        """
        Determines whether there is overlap between two ranges.
        Args:
            range1 (list): First range with two float values.
            range2 (list): Second raneg with float values.
        Returns:
            Boolean value indicating whether the sections overlap or not.
        """
        min1, max1 = min(range1), max(range1)
        min2, max2 = min(range2), max(range2)
        overlap = max(min1, min2) <= min(max1, max2)
        return overlap

    def __update_section(self, index: int, km_range: list = None, props: dict = None, geom: LineString = None):
        """
        ...
        Prints log of update.
        """
        assert any(km_range, props, geom), 'No update required.'
        if props:
            self.sections[index]['properties'].update(props)
        if km_range:
            self.sections[index]['km_range'] = km_range
        if geom:
            self.sections[index]['geometry'] = geom

        self.__log_section_change(index)

    def __add_section(self, side: str, km_range: list[int], prop: dict, geom: LineString):
        """
        Adds a section to the sections variable and increases the index.
        Args:
            side (str): Side of the road ('L' or 'R').
            kmrange (list[int]): Start and end registration kilometre.
            prop (dict): All properties that belong to the section.
            geom (LineString): The geometry of the section.
        Prints:
            Newly added section properties to log window.
        """
        self.sections[self.section_index] = {'side': side,
                                             'km_range': sorted(km_range),
                                             'properties': prop,
                                             'geometry': geom}
        print("Section", self.section_index, ":", side, km_range, prop)
        self.section_index += 1

    def __log_section(self, index: int):
        print("Added a new section at index", index, "with:",
              self.sections[index]['side'],
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

    def __log_section_change(self, index: int):
        print("Adjusted the properties of section", index, "to:",
              self.sections[index]['side'],
              self.sections[index]['km_range'],
              self.sections[index]['properties'],
              self.sections[index]['geometry'])

    def __check_overlap(self, geometry1: geometry, geometry2: geometry) -> tuple[geometry, bool]:
        """
        Finds the overlap geometry between two Shapely geometries.
        Args:
            geometry1 (geometry): The first Shapely geometry.
            geometry2 (geometry): The second Shapely geometry.
        Returns:
            tuple[geometry, bool]: A tuple containing the overlap geometry
            and a boolean indicating whether there is an overlap (True) or not (False).
        Note:
            The function uses the `intersection` method from Shapely to compute the overlap
            between the two geometries.
            If the geometries do not overlap or have only a point of intersection, the function
            returns an empty LineString and False.
        """
        overlap_geometry = intersection(geometry1, geometry2)

        if overlap_geometry.is_empty:
            return LineString([]), False
        else:
            if isinstance(overlap_geometry, MultiLineString):
                return self.ConvertToLineString(overlap_geometry), True
            elif isinstance(overlap_geometry, LineString):
                return overlap_geometry, True
            else:
                return LineString([]), False

    @staticmethod
    def convert_to_LineString(mls: MultiLineString) -> LineString:
        """
        Converts MultiLineString objects resulting fron the intersection function into LineStrings.
        Args:
            mls (MultiLineString): The MultiLineString geometry.
        Returns:
            LineString: LineString representation of the same MultiLineString.
        Note:
            The function expects a very specific format of MultiLineStrings.
            An assert statement is added to help prevent other uses.
        """
        assert all([get_num_points(line) == 2 for line in mls.geoms]), 'Unexpected line length.'
        coords = [get_point(line, 0) for line in mls.geoms]
        coords.append(get_point(mls.geoms[-1], 1))
        return LineString(coords)

    def get_properties_at(self, km: float, side: str) -> dict:
        """
        Find the properties of a road section at a specific km.
        Args:
            km (float): Kilometer point to retrieve the road section for.
            side (str): Side of the road to retrieve the road section for.
        Returns:
            dict: Attributes of the road section at the specified kilometer point.
        """
        sections = []
        for section_index, section_info in self.sections.items():
            if section_info['side'] == side:
                if min(section_info['km_range']) <= km <= max(section_info['km_range']):
                    sections.append(section_info['properties'])
        if len(sections) > 1:
            print("Warning: This slice has two roadlines.")
        print(sections)
        return sections

        # assert sum([]) == 1, 'Alert: more than one kantstroken property active'
