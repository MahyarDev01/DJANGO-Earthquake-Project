import pandas as pd
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__)) 
src_dir = os.path.dirname(current_dir) 
project_root = os.path.dirname(src_dir) 
sys.path.append(project_root) 

from configs import JAPAN_EMSC_CSV, JAPAN_GEOFON_CSV, JAPAN_USGS_CSV, JAPAN_DATASET_CSV 
from Src.Database.db_connection import get_engine

def import_data_to_db(): 
    print("Connecting to the database...") 
    
    engine = get_engine() 
    
    files_to_import = {
        'EMSC': JAPAN_EMSC_CSV,
        'GEOFON': JAPAN_GEOFON_CSV,
        'USGS': JAPAN_USGS_CSV,
        'DEFAULT_DATASET': JAPAN_DATASET_CSV
    } 

    for source_name, file_path in files_to_import.items(): 
        if os.path.exists(file_path): 
            print(f"Reading raw data from {source_name}...") 
            
            try: 
                df = pd.read_csv(file_path)
            except pd.errors.EmptyDataError:
                print(f"⚠️ File {source_name} is empty. Skipping...")
                continue

            rename_dict = {} 
            if 'date' in df.columns: 
                rename_dict['date'] = 'time' 
            if 'region' in df.columns:
                rename_dict['region'] = 'place' 
            if 'mag' in df.columns:
                rename_dict['mag'] = 'magnitude' 
            
            if rename_dict: 
                df = df.rename(columns=rename_dict) 
            
            df['source'] = source_name 
            
            db_columns = ['magnitude', 'depth', 'longitude', 'latitude', 'time', 'place', 'source'] 
            available_columns = [col for col in db_columns if col in df.columns] 
            df = df[available_columns] 
            
            try: 
                df.to_sql('earthquakes', engine, if_exists='append', index=False) 
                print(f"✅ {len(df)} rows from {source_name} successfully loaded into the database!") 
            except Exception as e: 
                print(f"❌ Error loading {source_name}: {e}") 
        else: 
            print(f"⚠️ File not found: {file_path}. Skipping...")

if __name__ == "__main__":
    import_data_to_db()