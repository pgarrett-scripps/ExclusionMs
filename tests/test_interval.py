import sys
import unittest

from exclusionms.components import ExclusionInterval

interval1 = ExclusionInterval(interval_id='PEPTIDE',
                              charge=1,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=2000,
                              max_rt=2001,
                              min_ook0=3000,
                              max_ook0=3001,
                              min_intensity=4000,
                              max_intensity=4001)

interval2 = ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=None,
                              max_mass=None,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None)


class TestExclusionList(unittest.TestCase):

    def test_create(self):
        self.assertEqual(interval1.interval_id, 'PEPTIDE')
        self.assertEqual(interval1.charge, 1)
        self.assertEqual(interval1.min_mass, 1000)
        self.assertEqual(interval1.max_mass, 1001)
        self.assertEqual(interval1.min_rt, 2000)
        self.assertEqual(interval1.max_rt, 2001)
        self.assertEqual(interval1.min_ook0, 3000)
        self.assertEqual(interval1.max_ook0, 3001)
        self.assertEqual(interval1.min_intensity, 4000)
        self.assertEqual(interval1.max_intensity, 4001)

    def test_none(self):
        self.assertEqual(interval2.interval_id, None)
        self.assertEqual(interval2.charge, None)
        self.assertEqual(interval2.min_mass, sys.float_info.min)
        self.assertEqual(interval2.max_mass, sys.float_info.max)
        self.assertEqual(interval2.min_rt, sys.float_info.min)
        self.assertEqual(interval2.max_rt, sys.float_info.max)
        self.assertEqual(interval2.min_ook0, sys.float_info.min)
        self.assertEqual(interval2.max_ook0, sys.float_info.max)
        self.assertEqual(interval2.min_intensity, sys.float_info.min)
        self.assertEqual(interval2.max_intensity, sys.float_info.max)

    def test_interval_envelope(self):
        self.assertTrue(interval1.is_enveloped_by(interval2))
        self.assertFalse(interval2.is_enveloped_by(interval1))

        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=1,
                                  min_mass=999,
                                  max_mass=1002,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))

        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=1,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=999,
                                  max_mass=1002,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))
