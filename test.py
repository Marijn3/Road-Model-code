import unittest
from functions import *


def makeData(rijstroken_data, kantstroken_data) -> dict:
    return {'Rijstroken': rijstroken_data,
            'Kantstroken': kantstroken_data,
            'Mengstroken': pd.DataFrame(),
            'Maximum snelheid': pd.DataFrame(),
            'Rijstrooksignaleringen': pd.DataFrame()}


class TestRoadModel(unittest.TestCase):

    def setUp(self):
        self.road_model = RoadModel()
        self.dfl = DataFrameLoader()

        # Add test data
        self.rijstroken_data = pd.DataFrame({'IZI_SIDE': ['R', 'R'],
                                             'BEGINKM': [0, 2],
                                             'EINDKM': [2, 4],
                                             'nRijstroken': [2, 2],
                                             'VNRWOL': [1, 1],
                                             'geometry': [LineString([[0, 0], [2000, 0]]),
                                                          LineString([[2000, 0], [4000, 0]])]})

    def test_equal_sections(self):
        print('Test equal sections:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [0, 2],
                                         'EINDKM': [2, 4],
                                         'OMSCHR': ['Vluchtstrook', 'Puntstuk'],
                                         'VNRWOL': [3, 3],
                                         'geometry': [LineString([[0, 0], [2000, 0]]),
                                                      LineString([[2000, 0], [4000, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 2)
        self.assertEqual(len(self.road_model.sections[0]['properties']), 3)

    def test_half_equal_sections(self):
        print('Test half equal sections:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [-1, 3],
                                         'EINDKM': [1, 5],
                                         'OMSCHR': ['Vluchtstrook', 'Puntstuk'],
                                         'VNRWOL': [3, 3],
                                         'geometry': [LineString([[-1000, 0], [1000, 0]]),
                                                      LineString([[3000, 0], [5000, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 6)
        self.assertDictEqual(self.road_model.get_properties_at(0.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(1.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})

    def test_neither_equal_sections(self):  # Should not be added
        print('Test neither equal sections:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [5],
                                         'EINDKM': [7],
                                         'OMSCHR': ['Vluchtstrook'],
                                         'VNRWOL': [2],
                                         'geometry': [LineString([[5000, 0], [7000, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 2)
        self.assertDictEqual(self.road_model.get_properties_at(3, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})

    def test_double_overlap_sections(self):
        print('Test double overlap sections:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [1.6],
                                         'EINDKM': [3.4],
                                         'OMSCHR': ['Vluchtstrook'],
                                         'VNRWOL': [3],
                                         'geometry': [LineString([[1600, 0], [3400, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 4)
        self.assertDictEqual(self.road_model.get_properties_at(1.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(1.7, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(3.3, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(3.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})

    def test_reversed_sections(self):
        print('Test reversed sections:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [1],
                                         'EINDKM': [4],
                                         'OMSCHR': ['Vluchtstrook'],
                                         'VNRWOL': [3],
                                         'geometry': [LineString([[4000, 0], [1000, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 3)
        self.assertDictEqual(self.road_model.get_properties_at(0.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(1.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})

    def test_segmented_sections(self):
        print('Test segmented sections:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [1],
                                         'EINDKM': [3.2],
                                         'OMSCHR': ['Vluchtstrook'],
                                         'VNRWOL': [3],
                                         'geometry': [LineString([[1000, 0], [1500, 0], [2500, 0], [3200, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 4)
        self.assertDictEqual(self.road_model.get_properties_at(1.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(3.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})

    def test_two_remainders(self):
        print('Test two remainders:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [0.7],
                                         'EINDKM': [1.2],
                                         'OMSCHR': ['Vluchtstrook'],
                                         'VNRWOL': [3],
                                         'geometry': [LineString([[700, 0], [1200, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 4)
        self.assertDictEqual(self.road_model.get_properties_at(1, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(1.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(3.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook'})

    def test_two_remainders_reverse(self):
        print('Test two remainders reverse:')
        kantstroken_data = pd.DataFrame({'BEGINKM': [-2],
                                         'EINDKM': [8],
                                         'OMSCHR': ['Vluchtstrook'],
                                         'VNRWOL': [3],
                                         'geometry': [LineString([[-2000, 0], [8000, 0]])]})
        self.dfl.data = makeData(self.rijstroken_data, kantstroken_data)
        self.road_model.import_dataframes(self.dfl)

        self.assertEqual(len(self.road_model.sections), 4)
        self.assertDictEqual(self.road_model.get_properties_at(1, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        self.assertDictEqual(self.road_model.get_properties_at(3.5, 'R'),
                             {1: 'Rijstrook', 2: 'Rijstrook', 3: 'Vluchtstrook'})
        # self.assertRaises(IndexError, self.road_model.get_properties_at(6, 'R'))


if __name__ == '__main__':
    unittest.main()
