import unittest
from functions import *


class TestGeneral(unittest.TestCase):

    def test_range_diff(self):
        print('Test range function')
        diff = get_range_diff([1, 8], [2, 5], 2500)
        self.assertEqual(diff, [5, 8])

        diff = get_range_diff([9, 1], [2, 12], 4000)
        self.assertEqual(diff, [9, 12])

        diff = get_range_diff([20, 25], [2, 22], 2000)
        self.assertEqual(diff, [22, 25])

        diff = get_range_diff([4, 6], [1, 10], 3200)
        print(diff)
        self.assertEqual(diff, [1, 4])

    def test_rp_processing(self):
        print('Test registration point processing')
        range1 = [1, 2]
        range2 = [1, 3]
        midpoint, overlapping_point, unique_points, extreme_point = process_registration_points(range1, range2)
        self.assertEqual(midpoint, 2)
        self.assertEqual(overlapping_point, 1)
        self.assertEqual(unique_points, [2, 3])
        self.assertEqual(extreme_point, 3)

        print('Test registration point processing, different points')
        range1 = [9, 4]
        range2 = [6, 4]
        midpoint, overlapping_point, unique_points, extreme_point = process_registration_points(range1, range2)
        self.assertEqual(midpoint, 6)
        self.assertEqual(overlapping_point, 4)
        self.assertEqual(unique_points, [6, 9])
        self.assertEqual(extreme_point, 9)


class TestRoadModel(unittest.TestCase):

    def test_equal_sections(self):
        print('Test equal sections')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                        'BEGINKM': [0, 1],
                                        'EINDKM': [1, 2],
                                        'nLanes': [2, 2],
                                        'geometry': [LineString([[0, 0], [1000, 0]]),
                                                     LineString([[1000, 0], [1000, 1000]]) ]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                         'BEGINKM': [0, 1],
                                         'EINDKM': [1, 2],
                                         'Vluchtstrook': [True, False],
                                         'Spitsstrook': [False, False],
                                         'Puntstuk': [False, True],
                                         'geometry': [LineString([[0, 0], [1000, 0]]),
                                                      LineString([[1000, 0], [1000, 1000]]) ]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 2)

    def test_half_equal_sections(self):
        print('Test half equal sections')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                        'BEGINKM': [0, 1, 1],
                                        'EINDKM': [1, 3, 2],
                                        'nLanes': [2, 2, 1],
                                        'geometry': [LineString([[0, 0], [1000, 0]]),
                                                     LineString([[1000, 0], [1000, 2000]]),
                                                     LineString([[1000, 0], [2000, 0]]) ]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                         'BEGINKM': [0, 1, 1],
                                         'EINDKM': [1, 2, 2],
                                         'Vluchtstrook': [True, False, True],
                                         'Spitsstrook': [False, False, False],
                                         'Puntstuk': [False, True, False],
                                         'geometry': [LineString([[0, 0], [1000, 0]]),
                                                      LineString([[1000, 0], [1000, 1]]),
                                                      LineString([[1000, 0], [2000, 0]]) ]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 4)
        self.assertDictEqual(road_model.get_properties_at(2.5, 'L')[0],
                             {'nLanes': 2},
                             "Incorrect lane properties.")

    def test_half_equal_sections_reverse(self):
        print('Test half equal sections reversed')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                        'BEGINKM': [0, 1, 1],
                                        'EINDKM': [1, 2, 2],
                                        'nLanes': [2, 2, 1],
                                        'geometry': [LineString([[0, 0], [1000, 0]]),
                                                     LineString([[1000, 0], [1000, 1]]),
                                                     LineString([[1000, 0], [2000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L', 'L'],
                                         'BEGINKM': [0, 1, 1],
                                         'EINDKM': [1, 2, 3],
                                         'Vluchtstrook': [True, False, True],
                                         'Spitsstrook': [False, False, False],
                                         'Puntstuk': [False, True, False],
                                         'geometry': [LineString([[0, 0], [1000, 0]]),
                                                      LineString([[1000, 0], [1000, 1]]),
                                                      LineString([[1000, 0], [3000, 0]])]})

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
        print('Test neither equal sections')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                        'BEGINKM': [0],
                                        'EINDKM': [2],
                                        'nLanes': [2],
                                        'geometry': [LineString([[0, 0], [2000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                         'BEGINKM': [1],
                                         'EINDKM': [4],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [LineString([[1000, 0], [4000, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 3)
        self.assertDictEqual(road_model.get_properties_at(1.5, 'L')[0],
                             {'nLanes': 2, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')

    def test_double_overlap_sections(self):
        print('Test double overlap sections')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                        'BEGINKM': [0, 2],
                                        'EINDKM': [2, 5],
                                        'nLanes': [1, 2],
                                        'geometry': [LineString([[0, 0], [2000, 0]]),
                                                     LineString([[2000, 0], [5000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                         'BEGINKM': [1],
                                         'EINDKM': [3.2],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [LineString([[1000, 0], [3200, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 4)
        self.assertDictEqual(road_model.get_properties_at(1.5, 'L')[0],
                             {'nLanes': 1, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')
        self.assertDictEqual(road_model.get_properties_at(3.5, 'L')[0],
                             {'nLanes': 2},
                             'Incorrect lane properties')

    def test_reversed_sections(self):
        print('Test reversed sections')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['R', 'R'],
                                        'BEGINKM': [2, 5],
                                        'EINDKM': [0, 2],
                                        'nLanes': [2, 1],
                                        'geometry': [LineString([[2000, 0], [0, 0]]),
                                                     LineString([[5000, 0], [2000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['R'],
                                         'BEGINKM': [3.2],
                                         'EINDKM': [1],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [LineString([[3200, 0], [1000, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 4)
        self.assertDictEqual(road_model.get_properties_at(1.5, 'R')[0],
                             {'nLanes': 2, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')
        self.assertDictEqual(road_model.get_properties_at(3.5, 'R')[0],
                             {'nLanes': 1},
                             'Incorrect lane properties')

    def test_segmented_sections(self):
        print('Test segmented sections')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L', 'L'],
                                        'BEGINKM': [0, 2],
                                        'EINDKM': [2, 5],
                                        'nLanes': [2, 1],
                                        'geometry': [LineString([[0, 0], [500, 0], [1000, 0], [1500, 0], [2000, 0]]),
                                                     LineString([[2000, 0], [2500, 0], [3500, 0], [4000, 0], [5000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                         'BEGINKM': [1],
                                         'EINDKM': [3.2],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [LineString([[1000, 0], [1500, 0], [2000, 0], [2500, 0], [3200, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 4)
        self.assertDictEqual(road_model.get_properties_at(1.5, 'L')[0],
                             {'nLanes': 2, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')
        self.assertDictEqual(road_model.get_properties_at(3.5, 'L')[0],
                             {'nLanes': 1},
                             'Incorrect lane properties')

    def test_two_remainders(self):
        print('Test two remainders')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                        'BEGINKM': [0],
                                        'EINDKM': [6],
                                        'nLanes': [5],
                                        'geometry': [LineString([[0, 0], [6000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                         'BEGINKM': [1],
                                         'EINDKM': [3],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [LineString([[1000, 0], [1500, 0], [2000, 0], [2500, 0], [3000, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 3)
        self.assertDictEqual(road_model.get_properties_at(2, 'L')[0],
                             {'nLanes': 5, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')
        self.assertDictEqual(road_model.get_properties_at(3.5, 'L')[0],
                             {'nLanes': 5},
                             'Incorrect lane properties')

    def test_two_remainders_reverse(self):
        print('Test two remainders reverse')
        road_model = RoadModel()
        dfl = DataFrameLoader()

        # Add test data
        rijstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                        'BEGINKM': [1],
                                        'EINDKM': [3],
                                        'nLanes': [5],
                                        'geometry': [LineString([[1000, 0], [3000, 0]])]})

        kantstroken_data = pd.DataFrame({'IZI_SIDE': ['L'],
                                         'BEGINKM': [0],
                                         'EINDKM': [5],
                                         'Vluchtstrook': [True],
                                         'Spitsstrook': [False],
                                         'Puntstuk': [False],
                                         'geometry': [LineString([[0, 0], [2000, 0], [5000, 0]])]})

        dfl.data = {'Rijstroken': rijstroken_data, 'Kantstroken': kantstroken_data}

        road_model.import_dataframes(dfl)

        self.assertEqual(len(road_model.sections), 3)
        self.assertDictEqual(road_model.get_properties_at(2, 'L')[0],
                             {'nLanes': 5, 'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')
        self.assertDictEqual(road_model.get_properties_at(4, 'L')[0],
                             {'Vluchtstrook': True, 'Spitsstrook': False, 'Puntstuk': False},
                             'Incorrect lane properties')


if __name__ == '__main__':
    unittest.main()
