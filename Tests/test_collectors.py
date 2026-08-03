import unittest
import os
import sys 
from datetime import datetime, timedelta 

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

import pandas as pd

from configs import JAPAN_GEOFON_CSV , JAPAN_EMSC_CSV
from Src.Data_collection import usgs_api
from Src.Data_collection import geofon_scraping
from Src.Data_collection import emsc_scraping

class TestUSGSAPI(unittest.TestCase):

    def test_build_params(self):
        result = usgs_api.build_params()
        self.assertEqual(result['format'],'csv')
        self.assertEqual(result["minmagnitude"] , 1)

    def test_download_usgs_data(self):
        params = usgs_api.build_params()
        response = usgs_api.download_usgs_data(params)

        self.assertGreater(len(response.text) , 0 )
        self.assertIn('latitude' , response.text)
        self.assertEqual(response.status_code, 200)


    def test_save_csv(self):
        params = usgs_api.build_params()
        response = usgs_api.download_usgs_data(params)

        usgs_api.save_csv(response,'test.csv')
        try:
            self.assertTrue(os.path.exists('test.csv'))

            with open('test.csv' ,'r',  encoding='utf-8') as f:
                self.assertEqual(f.read(), response.text)
        finally:
            if os.path.exists('test.csv'):
                os.remove('test.csv')


class TestGEOFONSCRAPING(unittest.TestCase):
  
    def test_geofon_and_csv_created(self):
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days = 30)

        result = geofon_scraping.geofon_data_earthquake_scrape(start_date,
                                                    end_date,
                                                    24,
                                                    46,
                                                    123,
                                                    146,
                                                    1)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(JAPAN_GEOFON_CSV))

        df = pd.read_csv(JAPAN_GEOFON_CSV)

        self.assertIn('date' , df.columns)
        self.assertIn('latitude' , df.columns)
        self.assertIn('longitude' , df.columns)
        self.assertIn('magnitude' , df.columns)
        self.assertIn('magtype' , df.columns)
        self.assertIn('region' , df.columns)
        self.assertIn('depth' , df.columns)

        self.assertGreater(len(df),0)

            
class TestEMSCSCRAPING(unittest.TestCase):

    def test_emsc_data_earthquake_scrape(self):
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days = 30)

        # اصلاح: اول start_date و بعد end_date
        result = emsc_scraping.emsc_data_earthquake_scrape(
            start_date, 
            end_date, 
            24, 46, 123, 146, 1
        )
        self.assertTrue(result)
        self.assertTrue(os.path.exists(JAPAN_EMSC_CSV))

        df = pd.read_csv(JAPAN_EMSC_CSV)
        self.assertGreater(len(df),0)

        self.assertIn('date' , df.columns)
        self.assertIn('latitude' , df.columns)
        self.assertIn('longitude' , df.columns)
        self.assertIn('magnitude' , df.columns)
        self.assertIn('magtype' , df.columns)
        self.assertIn('region' , df.columns)
        self.assertIn('depth' , df.columns)
        
if __name__ == "__main__":
    unittest.main()
