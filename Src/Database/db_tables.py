import os
import sys
from db_connection import db_cursor

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.append(project_root)


def create_tables():    
    create_query = """
    CREATE TABLE IF NOT EXISTS earthquakes (
        id SERIAL PRIMARY KEY,
        magnitude VARCHAR(50),
        depth VARCHAR(50),
        longitude VARCHAR(50),
        latitude VARCHAR(50),
        time VARCHAR(100),
        place VARCHAR(255),
        source VARCHAR(50)
    );
    """

    try:
        with db_cursor() as cur:
            cur.execute(create_query)
            
        print("✅ The `earthquakes` table was successfully created.")
        
    except Exception as e:
        print(f"❌ Error in run query and create table: {e}")

if __name__ == "__main__":
    create_tables()