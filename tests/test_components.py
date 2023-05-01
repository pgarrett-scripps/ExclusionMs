import unittest

from exclusionms.components import ExclusionInterval, ExclusionPoint

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
        self.assertEqual(interval2.min_mass, None)
        self.assertEqual(interval2.max_mass, None)
        self.assertEqual(interval2.min_rt, None)
        self.assertEqual(interval2.max_rt, None)
        self.assertEqual(interval2.min_ook0, None)
        self.assertEqual(interval2.max_ook0, None)
        self.assertEqual(interval2.min_intensity, None)
        self.assertEqual(interval2.max_intensity, None)

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

    def test_interval_envelope_equal(self):
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
                                  charge=1,
                                  min_mass=1000,
                                  max_mass=1001,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))

    def test_interval_envelope_lower_bounds(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=1,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=1000,
                              max_rt=1001,
                              min_ook0=1000,
                              max_ook0=1001,
                              min_intensity=1000,
                              max_intensity=1001).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=1,
                                  min_mass=1000,
                                  max_mass=1002,
                                  min_rt=1000,
                                  max_rt=1002,
                                  min_ook0=1000,
                                  max_ook0=1002,
                                  min_intensity=1000,
                                  max_intensity=1002)))

    def test_interval_envelope_upper_bounds(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=1,
                              min_mass=1000,
                              max_mass=1001,
                              min_rt=1000,
                              max_rt=1001,
                              min_ook0=1000,
                              max_ook0=1001,
                              min_intensity=1000,
                              max_intensity=1001).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=1,
                                  min_mass=999,
                                  max_mass=1001,
                                  min_rt=999,
                                  max_rt=1001,
                                  min_ook0=999,
                                  max_ook0=1001,
                                  min_intensity=999,
                                  max_intensity=1001)))

    def test_interval_envelope_equal_none(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=None,
                              max_mass=None,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=None,
                                  max_mass=None,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))

        def test_interval_envelope_none_with_charge(self):
            self.assertTrue(
                ExclusionInterval(interval_id=None,
                                  charge=2,
                                  min_mass=None,
                                  max_mass=None,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None).is_enveloped_by(
                    ExclusionInterval(interval_id=None,
                                      charge=None,
                                      min_mass=None,
                                      max_mass=None,
                                      min_rt=None,
                                      max_rt=None,
                                      min_ook0=None,
                                      max_ook0=None,
                                      min_intensity=None,
                                      max_intensity=None)))

            self.assertFalse(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=None,
                                  max_mass=None,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None).is_enveloped_by(
                    ExclusionInterval(interval_id=None,
                                      charge=2,
                                      min_mass=None,
                                      max_mass=None,
                                      min_rt=None,
                                      max_rt=None,
                                      min_ook0=None,
                                      max_ook0=None,
                                      min_intensity=None,
                                      max_intensity=None)))

    def test_interval_envelope_none_with_lower(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=1000,
                              max_mass=None,
                              min_rt=1000,
                              max_rt=None,
                              min_ook0=1000,
                              max_ook0=None,
                              min_intensity=1000,
                              max_intensity=None).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=None,
                                  max_mass=None,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))

        self.assertFalse(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=None,
                              max_mass=None,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=1000,
                                  max_mass=None,
                                  min_rt=1000,
                                  max_rt=None,
                                  min_ook0=1000,
                                  max_ook0=None,
                                  min_intensity=1000,
                                  max_intensity=None)))

    def test_interval_envelope_none_with_upper(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=None,
                              max_mass=1000,
                              min_rt=None,
                              max_rt=1000,
                              min_ook0=None,
                              max_ook0=1000,
                              min_intensity=None,
                              max_intensity=1000).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=None,
                                  max_mass=None,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))

        self.assertFalse(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=None,
                              max_mass=None,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None).is_enveloped_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=None,
                                  max_mass=1000,
                                  min_rt=None,
                                  max_rt=1000,
                                  min_ook0=None,
                                  max_ook0=1000,
                                  min_intensity=None,
                                  max_intensity=1000)))

    def test_interval_envelope_id(self):
        self.assertTrue(interval1.is_enveloped_by(interval2))
        self.assertFalse(interval2.is_enveloped_by(interval1))

        e1 = ExclusionInterval(interval_id='1',
                               charge=None,
                               min_mass=0,
                               max_mass=1600,
                               min_rt=None,
                               max_rt=None,
                               min_ook0=None,
                               max_ook0=None,
                               min_intensity=None,
                               max_intensity=None)
        e2 = ExclusionInterval(interval_id='1',
                               charge=None,
                               min_mass=None,
                               max_mass=None,
                               min_rt=None,
                               max_rt=None,
                               min_ook0=None,
                               max_ook0=None,
                               min_intensity=None,
                               max_intensity=None)
        res = e1.is_enveloped_by(e2)
        self.assertTrue(res)

    def test_none_point_is_bounded_by_none_interval(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=None,
                              min_mass=None,
                              max_mass=None,
                              min_rt=None,
                              max_rt=None,
                              min_ook0=None,
                              max_ook0=None,
                              min_intensity=None,
                              max_intensity=None).contains_point(
                ExclusionPoint(charge=None,
                               mass=None,
                               rt=None,
                               ook0=None,
                               intensity=None)))

        self.assertTrue(
            ExclusionPoint(charge=None,
                           mass=None,
                           rt=None,
                           ook0=None,
                           intensity=None).is_bounded_by(
                ExclusionInterval(interval_id=None,
                                  charge=None,
                                  min_mass=None,
                                  max_mass=None,
                                  min_rt=None,
                                  max_rt=None,
                                  min_ook0=None,
                                  max_ook0=None,
                                  min_intensity=None,
                                  max_intensity=None)))

    def test_none_point_is_bounded_by_interval(self):

        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=1,
                              min_mass=999,
                              max_mass=1000,
                              min_rt=999,
                              max_rt=1000,
                              min_ook0=999,
                              max_ook0=1000,
                              min_intensity=999,
                              max_intensity=1000).contains_point(
                ExclusionPoint(charge=None,
                               mass=None,
                               rt=None,
                               ook0=None,
                               intensity=None)))

        self.assertTrue(
            ExclusionPoint(charge=None,
                           mass=None,
                           rt=None,
                           ook0=None,
                           intensity=None).is_bounded_by(
                ExclusionInterval(interval_id=None,
                                  charge=1,
                                  min_mass=999,
                                  max_mass=1000,
                                  min_rt=999,
                                  max_rt=1000,
                                  min_ook0=999,
                                  max_ook0=1000,
                                  min_intensity=999,
                                  max_intensity=1000)))

    def test_point_is_bounded_by_interval(self):
        self.assertTrue(
            ExclusionInterval(interval_id=None,
                              charge=1,
                              min_mass=999,
                              max_mass=1000,
                              min_rt=999,
                              max_rt=1000,
                              min_ook0=999,
                              max_ook0=1000,
                              min_intensity=999,
                              max_intensity=1000).contains_point(
                ExclusionPoint(charge=1,
                               mass=999.5,
                               rt=999.5,
                               ook0=999.5,
                               intensity=999.5)))

        self.assertTrue(
            ExclusionPoint(charge=1,
                           mass=999.5,
                           rt=999.5,
                           ook0=999.5,
                           intensity=999.5).is_bounded_by(
                ExclusionInterval(interval_id=None,
                                  charge=1,
                                  min_mass=999,
                                  max_mass=1000,
                                  min_rt=999,
                                  max_rt=1000,
                                  min_ook0=999,
                                  max_ook0=1000,
                                  min_intensity=999,
                                  max_intensity=1000)))

if __name__ == '__main__':
    unittest.main()
