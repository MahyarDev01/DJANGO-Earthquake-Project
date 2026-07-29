import os
import sys
from configs import SCHEMA_SQL
from db_connection import db_cursor

# حل مشکل ایمپورت: معرفی ریشه پروژه به پایتون (سه مرحله به عقب)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.append(project_root)


def create_tables():
    """
    این تابع فایل create_schema.sql را از طریق مسیر تعریف شده در configs.py 
    می‌خواند و جدول earthquakes را ایجاد می‌کند.
    """
    

    if not os.path.exists(SCHEMA_SQL):
        print(f"Error : File '{SCHEMA_SQL}' Not Found.")
        return

    try:
        with open(SCHEMA_SQL, 'r', encoding='utf-8') as file:
            create_query = file.read()
            
        with db_cursor() as cur:
            cur.execute(create_query)
            
        print("✅ The `earthquakes` table was successfully created from the `create_schema.sql` file.")
        
    except Exception as e:
        print(f"❌ Error in run query and create table: {e}")

if __name__ == "__main__":
    create_tables()