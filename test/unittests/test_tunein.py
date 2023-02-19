import unittest

from tunein import TuneIn, TuneInStation


class TestTuneIn(unittest.TestCase):

    def test_featured(self):
        stations = list(TuneIn.featured())
        print(stations)
        self.assertTrue(len(stations) > 0)
        self.assertTrue(isinstance(stations[0], TuneInStation))


if __name__ == '__main__':
    unittest.main()
