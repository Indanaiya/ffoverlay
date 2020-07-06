import unittest
import eorzea_time
from eorzea_time import getEorzeaTime, getEorzeaTimeDecimal, timeUntilInEorzea
from unittest import mock


class EorzeaTimeTests(unittest.TestCase):
    def test_type_of_getEorzeaTimeDecimal(self):
        self.assertEqual(type(getEorzeaTimeDecimal()), type((0.0,0.0)))
    
    def test_type_of_getEorzeaTime(self):
        self.assertEqual(type(getEorzeaTime()), type((0,0)))
    
    def test_result_of_getEorzeaTime(self):
        self.assertEqual(int(getEorzeaTimeDecimal()[0]), getEorzeaTime()[0])#Test hours
        self.assertEqual(int(getEorzeaTimeDecimal()[1]), getEorzeaTime()[1])#Test minutes

    def test_timeUntilInEorzea(self):
        with mock.patch.object(eorzea_time, 'getEorzeaTimeDecimal') as m:
            m.return_value = (12,0)
            #Testing midnight
            self.assertEqual(timeUntilInEorzea(0), 2100)#Half a day is 35min = 2100s
            #Testing 0 hours
            self.assertEqual(timeUntilInEorzea(12), 0)
            #Testing tomorrow morning
            self.assertEqual(timeUntilInEorzea(3), 2625)
            #Testing later today
            self.assertEqual(timeUntilInEorzea(15), 525)
            with self.assertRaises(ValueError):
                timeUntilInEorzea(-1)
            with self.assertRaises(ValueError):
                timeUntilInEorzea(25)