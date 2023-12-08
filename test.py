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

        print('test complete -------------')
        self.assertEqual(len(road_model.sections), 2)
        # TODO: Add more assertions...

    def test_half_equal_sections(self):
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                        'BEGINKM': [0, 1],
                                        'EINDKM': [1, 3],
                                        'nLanes': [2, 2],
                                        'geometry': [shapely.LineString([[0, 0], [1, 0]]),
                                                     shapely.LineString([[1, 0], [1, 2]]) ]})

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

        print('test complete -------------')
        self.assertEqual(len(road_model.sections), 3)
        # TODO: Add more assertions...


if __name__ == '__main__':
    unittest.main()
