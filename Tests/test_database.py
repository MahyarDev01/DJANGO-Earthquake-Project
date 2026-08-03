import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from Src.Database import db_connection, db_tables, csv_to_db

class TestDatabaseModules(unittest.TestCase):

    @patch('Src.Database.db_connection.psycopg2.connect')
    def test_create_database_if_not_exists(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        db_connection.create_database_if_not_exists()
        
        mock_connect.assert_called()
        mock_cursor.execute.assert_called()

    @patch('Src.Database.db_tables.db_cursor')
    def test_create_tables(self, mock_db_cursor):
        mock_cursor = MagicMock()
        mock_db_cursor.return_value.__enter__.return_value = mock_cursor
        
        db_tables.create_tables()
        
        mock_db_cursor.assert_called()
        mock_cursor.execute.assert_called()

    @patch('pandas.DataFrame.to_sql')
    @patch('Src.Database.csv_to_db.pd.read_csv')
    @patch('Src.Database.csv_to_db.os.path.exists')
    def test_import_data_to_db(self, mock_exists, mock_read_csv, mock_to_sql):
        mock_exists.return_value = True
        dummy_df = pd.DataFrame({
            'mag': [5.0, 4.2],
            'depth': [10, 15],
            'region': ['Tokyo', 'Osaka'],
            'date': ['2026-08-01', '2026-08-02']
        })
        mock_read_csv.return_value = dummy_df
        
        csv_to_db.import_data_to_db()
        
        mock_read_csv.assert_called()
        mock_to_sql.assert_called()
        call_args = mock_to_sql.call_args
        self.assertIsNotNone(call_args)

    @patch('pandas.DataFrame.to_sql')
    @patch('Src.Database.csv_to_db.pd.read_csv')
    @patch('Src.Database.csv_to_db.os.path.exists')
    def test_import_data_empty_file_handling(self, mock_exists, mock_read_csv, mock_to_sql):
        mock_exists.return_value = True
        mock_read_csv.side_effect = pd.errors.EmptyDataError("No columns to parse from file")
        
        csv_to_db.import_data_to_db()
        
        mock_to_sql.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)