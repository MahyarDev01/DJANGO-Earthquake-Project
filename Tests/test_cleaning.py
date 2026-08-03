import os
import sys
import tempfile
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

import pandas as pd
from Src.Analysis import clean_data


class TestParsers(unittest.TestCase):


    def test_parse_magnitude_numeric(self):
        self.assertEqual(clean_data.parse_magnitude("5.1"), 5.1)
        self.assertEqual(clean_data.parse_magnitude('"4.8"'), 4.8)

    def test_parse_magnitude_words(self):
        self.assertEqual(clean_data.parse_magnitude("four"), 4.0)
        self.assertEqual(clean_data.parse_magnitude("four.nine"), 4.9)
        self.assertEqual(clean_data.parse_magnitude("five point three"), 5.3)

    def test_parse_magnitude_missing(self):
        self.assertIsNone(clean_data.parse_magnitude(""))
        self.assertIsNone(clean_data.parse_magnitude(None))

    def test_parse_depth_units(self):
        self.assertAlmostEqual(clean_data.parse_depth("10 km"), 10.0)
        self.assertAlmostEqual(clean_data.parse_depth("10 meters"), 0.01)
        self.assertAlmostEqual(clean_data.parse_depth("25 miles"), 40.23, places=1)

    def test_parse_depth_only_converts_units_no_plausibility_check(self):
        self.assertEqual(clean_data.parse_depth("-999"), -999.0)
        self.assertEqual(clean_data.parse_depth("2000"), 2000.0)

    def test_parse_coordinate_unknown_values(self):
        self.assertIsNone(clean_data.parse_coordinate("N/A"))
        self.assertIsNone(clean_data.parse_coordinate("UNKNOWN"))
        self.assertEqual(clean_data.parse_coordinate("35.68"), 35.68)

    def test_parse_time_multiple_formats(self):
        self.assertFalse(pd.isna(clean_data.parse_time("2025-09-15T12:45:30.123Z")))
        self.assertFalse(pd.isna(clean_data.parse_time("Sep 17, 2025, 14:10:05")))
        self.assertFalse(pd.isna(clean_data.parse_time("22/09/2025 11:05:21")))
        self.assertFalse(pd.isna(clean_data.parse_time("2025-10-08T14:20:10.Z")))


class TestCleanDataset(unittest.TestCase):

    def setUp(self):
        self.cdf = clean_data.clean_dataset()

    def test_clean_dataset_keeps_every_row(self):

        raw = pd.read_csv(clean_data.RAW_JAPAN_DATASET_CSV, dtype=str)
        self.assertEqual(len(self.cdf), len(raw))


    def test_clean_dataset_expected_columns(self):

        for col in ["time", "latitude", "longitude", "depth", "magnitude", "place"]:
            self.assertIn(col, self.cdf)

    def test_clean_dataset_unparseable_values_become_null_not_dropped(self):

        csv_text = (
            "time,latitude,longitude,depth,mag,place\n"
            "2025-09-15T12:45:30Z,35.68,139.69,10 km,not-a-number,Tokyo\n"
            "2025-09-16T08:22:05Z,UNKNOWN,140.10,15 km,5.1,Osaka\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_text)
            temp_path = f.name

        try:
            df = clean_data.clean_dataset(temp_path)
            self.assertEqual(len(df), 2, "both rows should be kept, none dropped")
            self.assertTrue(pd.isna(df.loc[0, "magnitude"]), "'not-a-number' should become NaN")
            self.assertTrue(pd.isna(df.loc[1, "latitude"]), "'UNKNOWN' should become NaN")
        finally:
            os.remove(temp_path)

    def test_clean_dataset_magnitude_is_numeric_where_present(self):
        non_null_mag = self.cdf["magnitude"].dropna()
        self.assertTrue(non_null_mag.apply(lambda v: isinstance(v, float)).all())


if __name__ == "__main__":
    unittest.main()