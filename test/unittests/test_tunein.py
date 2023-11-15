import io
import contextlib
import json
import sys
import unittest
from unittest.mock import patch


from tunein import TuneIn, TuneInStation
from tunein.cli import Cli

class TestTuneIn(unittest.TestCase):

    def test_featured(self):
        stations = list(TuneIn.featured())
        print(stations)
        self.assertTrue(len(stations) > 0)
        self.assertTrue(isinstance(stations[0], TuneInStation))
    
    def test_cli_table(self):
        """Test the CLI output table format."""
        testargs = ["tunein", "search", "kuow", "-f", "table"]
        cli = Cli()
        fhand = io.StringIO()
        with patch.object(sys, 'argv', testargs):
            with contextlib.redirect_stdout(fhand):
                cli.parse_args()
                cli.run()
        self.assertTrue("KUOW" in fhand.getvalue())
    
    def test_cli_json(self):
        """Test the CLI output json format."""
        testargs = ["tunein", "search", "kuow", "-f", "json"]
        cli = Cli()
        fhand = io.StringIO()
        with patch.object(sys, 'argv', testargs):
            with contextlib.redirect_stdout(fhand):
                cli.parse_args()
                cli.run()
        json_loaded = json.loads(fhand.getvalue())
        kuow = [i for i in json_loaded if i["title"] == "KUOW-FM"]
        self.assertTrue(len(kuow) == 1)


if __name__ == '__main__':
    unittest.main()
