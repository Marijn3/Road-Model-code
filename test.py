import unittest
import pandas as pd
from functions import *


class TestRoadModel(unittest.TestCase):

    def test_equal_sections(self):
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                        'BEGINKM': [0, 1],
                                        'EINDKM': [1, 2],
                                        'nLanes': [2, 2],
                                        'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                     shapely.LineString([[1, 0], [1, 1]]) ]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                         'BEGINKM': [0, 1],
                                         'EINDKM': [1, 2],
                                         'Vluchtstrook': [True, False],
                                         'Spitsstrook': [False, False],
                                         'Puntstuk': [False, True],
                                         'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                      shapely.LineString([[1, 0], [1, 1]]) ]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 2)
        # TODO: Add more assertions...

    def test_half_equal_sections(self):
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                        'BEGINKM': [0, 1, 1],
                                        'EINDKM': [1, 3, 2],
                                        'nLanes': [2, 2, 1],
                                        'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                     shapely.LineString([[1, 0], [1, 2]]),
                                                     shapely.LineString([[1, 0], [2, 0]]) ]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                         'BEGINKM': [0, 1, 1],
                                         'EINDKM': [1, 2, 2],
                                         'Vluchtstrook': [True, False, True],
                                         'Spitsstrook': [False, False, False],
                                         'Puntstuk': [False, True, False],
                                         'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                      shapely.LineString([[1, 0], [1, 1]]),
                                                      shapely.LineString([[1, 0], [2, 0]]) ]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 4)

        # road_model.get_properties_at(0.5, 'L')
        # road_model.get_properties_at(1.5, 'L')
        # road_model.get_properties_at(2.5, 'L')

        # TODO: Add more assertions...

    def test_half_equal_sections_reverse(self):
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                        'BEGINKM': [0, 1, 1],
                                        'EINDKM': [1, 2, 2],
                                        'nLanes': [2, 2, 1],
                                        'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                     shapely.LineString([[1, 0], [1, 1]]),
                                                     shapely.LineString([[1, 0], [2, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                         'BEGINKM': [0, 1, 1],
                                         'EINDKM': [1, 2, 3],
                                         'Vluchtstrook': [True, False, True],
                                         'Spitsstrook': [False, False, False],
                                         'Puntstuk': [False, True, False],
                                         'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                      shapely.LineString([[1, 0], [1, 1]]),
                                                      shapely.LineString([[1, 0], [3, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 4, "Unexpected amount of sections.")
        self.assertDictEqual(road_model.get_properties_at(0.5, 'L')[0],
                             {'nLanes': 2, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             "Incorrect lane properties.")
        self.assertDictEqual(road_model.get_properties_at(1.5, 'L')[0],
                             {'nLanes': 2, 'Vluchtstrook': False, 'Spitsstrook': False, 'Puntstuk': True},
                             "Incorrect lane properties.")
        self.assertDictEqual(road_model.get_properties_at(1.5, 'L')[1],
                             {'nLanes': 1, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             "Incorrect lane properties.")
        self.assertDictEqual(road_model.get_properties_at(2.5, 'L')[0],
                             {'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             "Incorrect lane properties.")

    def test_neither_equal_sections(self):
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                        'BEGINKM': [0],
                                        'EINDKM': [2],
                                        'nLanes': [2],
                                        'geometry': [shapely.LineString([[0, 0], [2, 0]]) ]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                         'BEGINKM': [1],
                                         'EINDKM': [3],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [shapely.LineString([[1, 0], [3, 0]]) ]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)


if __name__ == '__main__':
    unittest.main()
