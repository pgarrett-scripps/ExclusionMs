import unittest
from copy import deepcopy

from exclusionms.components import ExclusionInterval, ExclusionPoint
from exclusionms.db import MassIntervalTree as ExclusionList

messages = [
    ExclusionInterval(id='PEPTIDE',
                      charge=1,
                      min_mass=1000,
                      max_mass=1001,
                      min_rt=1000,
                      max_rt=1001,
                      min_ook0=1000,
                      max_ook0=1001,
                      min_intensity=1000,
                      max_intensity=1001),
    ExclusionInterval(id='PEPTIDE',
                      charge=1,
                      min_mass=1000,
                      max_mass=1001,
                      min_rt=1000,
                      max_rt=1002,
                      min_ook0=1000,
                      max_ook0=1001,
                      min_intensity=1000,
                      max_intensity=1001)
]


class TestExclusionList(unittest.TestCase):

    def setUp(self) -> None:
        self.exlist = ExclusionList()

    def test_add(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))

    def test_duplicate_add(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))

    def test_remove(self):
        self.exlist.remove(messages[0])
        self.assertEqual(0, len(self.exlist))

    def test_add_remove(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        tmp_msg = deepcopy(messages[0])
        self.exlist.remove(tmp_msg)
        self.assertEqual(0, len(self.exlist))

    def test_add_remove_bounds(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        tmp_msg = deepcopy(messages[0])
        tmp_msg.id = None
        self.exlist.remove(tmp_msg)
        self.assertEqual(0, len(self.exlist))

    def test_exclude(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_exclude_lower_mass(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000, rt=1000.5,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_exclude_upper_mass(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1001, rt=1000.5,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_exclude_lower_retention_time(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000,
                                                               ook0=1000.5, intensity=1000.5)))

    def test_exclude_upper_retention_time(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1001,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_exclude_lower_ook0(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000, intensity=1000.5)))

    def test_exclude_upper_ook0(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                                ook0=1001, intensity=1000.5)))

    def test_exclude_lower_intensity(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                               ook0=1000.5, intensity=1000)))

    def test_exclude_upper_intensity(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                                ook0=1000.5, intensity=1001)))

    def test_exclude_wrong_charge(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertFalse(self.exlist.is_excluded(ExclusionPoint(charge=2, mass=1000.5, rt=1000.5,
                                                                ook0=1000.5, intensity=1000.5)))

    def test_none_point_charge(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=None, mass=1000.5, rt=1000.5,
                                                   ook0=1000.5, intensity=1000.5)))

    def test_none_point_mass(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=None, rt=1000.5,
                                                   ook0=1000.5, intensity=1000.5)))

    def test_none_point_rt(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=None,
                                                   ook0=1000.5, intensity=1000.5)))

    def test_none_point_ook0(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                   ook0=None, intensity=1000.5)))

    def test_none_point_intensity(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5,
                                                   ook0=None, intensity=None)))

    def test_none_interval_attributes(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=1000,
                                                                                max_mass=1001,
                                                                                min_rt=1000,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=1001,
                                                                                min_rt=1000,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=1000,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=1001,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=1000,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=1001,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=1000,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=None,
                                                                                max_intensity=1001))))

        self.assertEqual(1, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=None,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=None,
                                                                                max_intensity=None))))

        self.assertEqual(0, len(self.exlist.query_by_interval(ExclusionInterval(id='PEPTIDE',
                                                                                charge=None,
                                                                                min_mass=2000,
                                                                                max_mass=None,
                                                                                min_rt=None,
                                                                                max_rt=None,
                                                                                min_ook0=None,
                                                                                max_ook0=None,
                                                                                min_intensity=None,
                                                                                max_intensity=None))))

    def test_save_load(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.exlist.save("tmp.pkl")
        self.exlist.clear()
        self.exlist.load("tmp.pkl")
        self.assertEqual(1, len(self.exlist))
        self.assertTrue(
            self.exlist.is_excluded(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5)))

    def test_query_by_id(self):
        self.exlist.add(messages[0])
        self.assertEqual(1, len(self.exlist))
        self.assertEqual(messages[0], self.exlist.query_by_id('PEPTIDE')[0])

    def test_exclusion_interval_equality(self):
        self.assertEqual(messages[0], messages[0])
        self.assertNotEqual(messages[0], messages[1])

    def test_exclusion_point_equality(self):
        self.assertEqual(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5),
                         ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5))
        self.assertNotEqual(ExclusionPoint(charge=1, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5),
                            ExclusionPoint(charge=2, mass=1000.5, rt=1000.5, ook0=None, intensity=1000.5))


if __name__ == '__main__':
    unittest.main()
