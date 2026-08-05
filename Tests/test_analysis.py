import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from Src.Analysis import sql_query
from Src.Database.db_connection import db_cursor


EXPECTED_SOURCES = {"EMSC", "GEOFON", "USGS", "DEFAULT_DATASET"}
EXPECTED_CATEGORIES = {"Weak", "Moderate", "Strong"}



# tasks 3-10 (Src/Analysis/clean_sql.py) -- checked via table state, because they print tables

class TestTableStructure(unittest.TestCase):

    def test_expected_columns_exist(self):
        with db_cursor() as cur:
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'earthquakes';
            """)
            columns = {row[0] for row in cur.fetchall()}
        expected = {
            "id", "magnitude", "depth", "longitude", "latitude",
            "time", "place", "source", "month", "category", "region",
        }
        self.assertTrue(expected.issubset(columns))

    def test_table_has_rows(self):
        with db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM earthquakes;")
            row_count = cur.fetchone()[0]
        self.assertGreater(row_count, 0)


class TestMissingValuesHandled(unittest.TestCase):


    def test_no_nulls_in_essential_columns(self):
        with db_cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) FROM earthquakes
                WHERE magnitude IS NULL OR magnitude::text = ''
                   OR depth IS NULL OR depth::text = ''
                   OR longitude IS NULL OR longitude::text = ''
                   OR latitude IS NULL OR latitude::text = ''
                   OR "time" IS NULL OR "time"::text = '';
            """)
            missing_count = cur.fetchone()[0]
        self.assertEqual(missing_count, 0)

    def test_missing_place_defaults_to_unknown(self):
        with db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM earthquakes WHERE place IS NULL OR place = '';")
            blank_place = cur.fetchone()[0]
        self.assertEqual(blank_place, 0)


class TestDuplicatesRemoved(unittest.TestCase):

    def test_no_duplicate_time_lat_lon(self):
        with db_cursor() as cur:
            cur.execute("""
                SELECT "time", latitude, longitude, COUNT(*)
                FROM earthquakes
                GROUP BY "time", latitude, longitude
                HAVING COUNT(*) > 1;
            """)
            duplicates = cur.fetchall()
        self.assertEqual(duplicates, [])



class TestColumnTypes(unittest.TestCase):

    def _column_type(self, column_name):
        with db_cursor() as cur:
            cur.execute("""
                SELECT data_type FROM information_schema.columns
                WHERE table_name = 'earthquakes' AND column_name = %s;
            """, (column_name,))
            return cur.fetchone()[0]

    def test_magnitude_and_depth_are_numeric(self):
        self.assertEqual(self._column_type("magnitude"), "double precision")
        self.assertEqual(self._column_type("depth"), "double precision")

    def test_time_is_timestamp(self):
        self.assertEqual(self._column_type("time"), "timestamp without time zone")


class TestMonthColumn(unittest.TestCase):

    def test_month_within_valid_range(self):
        with db_cursor() as cur:
            cur.execute("SELECT MIN(month), MAX(month) FROM earthquakes;")
            min_month, max_month = cur.fetchone()
        self.assertGreaterEqual(min_month, 1)
        self.assertLessEqual(max_month, 12)


class TestCategoryColumn(unittest.TestCase):

    def test_category_values_are_valid(self):
        with db_cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM earthquakes;")
            categories = {row[0] for row in cur.fetchall()}
        self.assertTrue(categories.issubset(EXPECTED_CATEGORIES))

    def test_category_matches_magnitude_boundaries(self):
        with db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM earthquakes WHERE category = 'Weak' AND magnitude >= 4;")
            bad_weak = cur.fetchone()[0]
            cur.execute("""
                SELECT COUNT(*) FROM earthquakes
                WHERE category = 'Moderate' AND (magnitude < 4 OR magnitude > 6);
            """)
            bad_moderate = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM earthquakes WHERE category = 'Strong' AND magnitude <= 6;")
            bad_strong = cur.fetchone()[0]
        self.assertEqual(bad_weak, 0)
        self.assertEqual(bad_moderate, 0)
        self.assertEqual(bad_strong, 0)


class TestRegionColumn(unittest.TestCase):

    def test_region_is_populated(self):
        with db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM earthquakes WHERE region IS NULL OR TRIM(region) = '';")
            blank_region = cur.fetchone()[0]
        self.assertEqual(blank_region, 0)


class TestCountByMonth(unittest.TestCase):

    def test_monthly_counts_sum_to_total(self):
        with db_cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM earthquakes WHERE month IS NOT NULL;")
            total = cur.fetchone()[0]
            cur.execute("""
                SELECT month, COUNT(*) FROM earthquakes
                WHERE month IS NOT NULL GROUP BY month;
            """)
            monthly_counts = cur.fetchall()
        self.assertEqual(sum(count for _, count in monthly_counts), total)


# tasks 11-17 (Src/Analysis/sql_query.py) -- read-only, call directly.
class TestRegionAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = sql_query.task11_region_analysis()

    def test_not_empty(self):
        self.assertGreater(len(self.rows), 0)

    def test_each_region_has_at_least_one_earthquake(self):
        self.assertTrue(all(row[1] > 0 for row in self.rows))

    def test_min_magnitude_not_greater_than_max(self):
        self.assertTrue(all(row[4] <= row[5] for row in self.rows))

    def test_min_depth_not_greater_than_max(self):
        self.assertTrue(all(row[6] <= row[7] for row in self.rows))

    def test_sorted_by_total_earthquakes_descending(self):
        counts = [row[1] for row in self.rows]
        self.assertEqual(counts, sorted(counts, reverse=True))


class TestRegionMonthCategoryAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = sql_query.task12_region_month_category_analysis()

    def test_not_empty(self):
        self.assertGreater(len(self.rows), 0)

    def test_month_within_valid_range(self):
        self.assertTrue(all(1 <= row[1] <= 12 for row in self.rows))

    def test_category_values_are_valid(self):
        categories = {row[2] for row in self.rows}
        self.assertTrue(categories.issubset(EXPECTED_CATEGORIES))


class TestTop10RecentStrongEarthquakes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = sql_query.task13_top_10_recent_strong_earthquakes()

    def test_returns_at_most_10(self):
        self.assertLessEqual(len(self.rows), 10)

    def test_all_magnitudes_above_6(self):
        self.assertTrue(all(row[4] > 6 for row in self.rows))

    def test_sorted_by_time_descending(self):
        times = [row[1] for row in self.rows]
        self.assertEqual(times, sorted(times, reverse=True))


class TestDangerousEarthquakes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = sql_query.task14_dangerous_earthquakes()

    def test_filter_is_correct(self):
        if self.rows:
            self.assertTrue(all(row[4] > 6 for row in self.rows))
            self.assertTrue(all(row[5] < 50 for row in self.rows))

    def test_sorted_by_magnitude_descending(self):
        magnitudes = [row[4] for row in self.rows]
        self.assertEqual(magnitudes, sorted(magnitudes, reverse=True))


class TestEarthquakeCountBySource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = sql_query.task15_earthquake_count_by_source()

    def test_covers_all_expected_sources(self):
        sources = {row[0] for row in self.rows}
        self.assertTrue(EXPECTED_SOURCES.issubset(sources))

    def test_every_source_has_positive_count(self):
        self.assertTrue(all(row[1] > 0 for row in self.rows))

    def test_sorted_by_count_descending(self):
        counts = [row[1] for row in self.rows]
        self.assertEqual(counts, sorted(counts, reverse=True))


class TestAverageMagnitudeByRegionSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rows = sql_query.task16_average_magnitude_by_region_source()

    def test_not_empty(self):
        self.assertGreater(len(self.rows), 0)

    def test_sorted_by_avg_magnitude_descending(self):
        averages = [row[2] for row in self.rows]
        self.assertEqual(averages, sorted(averages, reverse=True))


class TestIndexes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.index_names = set(sql_query.task17_create_indexes())

    def test_all_three_indexes_exist(self):
        expected = {
            "idx_earthquakes_time",
            "idx_earthquakes_magnitude",
            "idx_earthquakes_region",
        }
        self.assertEqual(self.index_names, expected)


if __name__ == "__main__":
    unittest.main()