import os
import sys

# تنظیم مسیر برای دسترسی به ماژول‌های دایرکتوری‌های دیگر (دقیقاً مشابه روش خودت)
current_dir = os.path.dirname(os.path.abspath(__file__)) 
src_dir = os.path.dirname(current_dir) 
project_root = os.path.dirname(src_dir) 
sys.path.append(project_root)

# ایمپورت کردن کانتکست منیجر دیتابیس که قبلاً نوشتی
from Src.Database.db_connection import db_cursor

def task3_report_table_structure():
    """
    تسک ۳: بررسی ساختار جدول، نوع داده هر ستون، تعداد رکوردها و تعداد ستون‌های جدول
    """
    print("\n" + "="*50)
    print("🚀 Task 3: Table Structure Report")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. دریافت تعداد کل رکوردهای جدول
            cur.execute("SELECT COUNT(*) FROM earthquakes;")
            total_rows = cur.fetchone()[0]
            
            # ۲. دریافت اطلاعات ستون‌ها (نام ستون و نوع داده) از اسکیما
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'earthquakes';
            """)
            columns_info = cur.fetchall()
            total_columns = len(columns_info)
            
            # چاپ گزارش
            print(f"📊 Total Rows: {total_rows}")
            print(f"📊 Total Columns: {total_columns}\n")
            print("📋 Columns Detail:")
            for col_name, data_type in columns_info:
                print(f"  - {col_name.ljust(15)} : {data_type}")
                
    except Exception as e:
        print(f"❌ Error in Task 3: {e}")


def task4_handle_null_values():
    """
    تسک ۴: شناسایی مقادیر گمشده (NULL و خالی) و حذف یا جایگذاری آن‌ها
    """
    print("\n" + "="*50)
    print("🛠️ Task 4: Handling NULL or Missing Values")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. شناسایی مقادیر گمشده (بررسی NULL یا رشته خالی)
            check_query = """
                SELECT 
                    SUM(CASE WHEN magnitude IS NULL OR magnitude = '' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN depth IS NULL OR depth = '' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN longitude IS NULL OR longitude = '' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN latitude IS NULL OR latitude = '' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN time IS NULL OR time = '' THEN 1 ELSE 0 END),
                    SUM(CASE WHEN place IS NULL OR place = '' THEN 1 ELSE 0 END)
                FROM earthquakes;
            """
            cur.execute(check_query)
            missing_report = cur.fetchone()
            
            print("🔍 Missing Values Report (Before Cleaning):")
            print(f"  - Magnitude: {missing_report[0]}")
            print(f"  - Depth:     {missing_report[1]}")
            print(f"  - Longitude: {missing_report[2]}")
            print(f"  - Latitude:  {missing_report[3]}")
            print(f"  - Time:      {missing_report[4]}")
            print(f"  - Place:     {missing_report[5]}\n")
            
            # ۲. حذف رکوردهایی که داده‌های حیاتی آن‌ها نامعتبر است
            delete_query = """
                DELETE FROM earthquakes
                WHERE magnitude IS NULL OR magnitude = ''
                   OR depth IS NULL OR depth = ''
                   OR longitude IS NULL OR longitude = ''
                   OR latitude IS NULL OR latitude = ''
                   OR time IS NULL OR time = '';
            """
            cur.execute(delete_query)
            deleted_rows = cur.rowcount
            print(f"🗑️ Deleted {deleted_rows} rows with missing critical data (magnitude, depth, coords, time).")
            
            # ۳. جایگذاری مقدار مناسب برای فیلد place (در صورت خالی بودن)
            update_query = """
                UPDATE earthquakes
                SET place = 'Unknown'
                WHERE place IS NULL OR place = '';
            """
            cur.execute(update_query)
            updated_rows = cur.rowcount
            if updated_rows > 0:
                print(f"✏️ Updated {updated_rows} rows with missing 'place' to 'Unknown'.")
                
    except Exception as e:
        print(f"❌ Error in Task 4: {e}")
        
        
def task5_remove_duplicates():
    """
    تسک ۵: شناسایی داده‌های تکراری و حذف آن‌ها 
    تا هر زلزله تنها یک بار در جدول ثبت شده باشد.
    """
    print("\n" + "="*50)
    print("🧹 Task 5: Removing Duplicate Records")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. بررسی اینکه چند گروه دیتای تکراری داریم (اختیاری جهت گزارش‌گیری)
            check_duplicates_query = """
                SELECT COUNT(*) 
                FROM (
                    SELECT time, latitude, longitude
                    FROM earthquakes
                    GROUP BY time, latitude, longitude
                    HAVING COUNT(*) > 1
                ) AS duplicates;
            """
            cur.execute(check_duplicates_query)
            duplicate_groups = cur.fetchone()[0]
            
            # ۲. حذف رکوردهای تکراری با نگه داشتن کمترین id برای هر رویداد یکتا
            delete_query = """
                DELETE FROM earthquakes
                WHERE id NOT IN (
                    SELECT MIN(id)
                    FROM earthquakes
                    GROUP BY time, latitude, longitude
                );
            """
            cur.execute(delete_query)
            deleted_rows = cur.rowcount
            
            print(f"🔍 Found {duplicate_groups} groups of duplicated events.")
            if deleted_rows > 0:
                print(f"🗑️ Deleted {deleted_rows} duplicate rows successfully.")
            else:
                print("✅ No duplicate rows found.")
                
    except Exception as e:
        print(f"❌ Error in Task 5: {e}")
        
        
def task6_convert_data_types():
    """
    تسک ۶: تبدیل نوع داده ستون‌های magnitude و depth به FLOAT 
    و ستون time به TIMESTAMP (معادل DATETIME در PostgreSQL)
    """
    print("\n" + "="*50)
    print("🔄 Task 6: Converting Data Types")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. اول داده‌های کثیف ستون time را تمیز می‌کنیم (نگه داشتن ۱۹ کاراکتر اول)
            clean_time_query = """
                UPDATE earthquakes
                SET time = LEFT(time, 19);
            """
            cur.execute(clean_time_query)
            
            # ۲. حالا که دیتای زمان استاندارد شد، نوع ستون‌ها را تغییر می‌دهیم
            alter_query = """
                ALTER TABLE earthquakes
                ALTER COLUMN magnitude TYPE FLOAT USING magnitude::double precision,
                ALTER COLUMN depth TYPE FLOAT USING depth::double precision,
                ALTER COLUMN time TYPE TIMESTAMP USING time::timestamp;
            """
            cur.execute(alter_query)
            print("✅ Data types for 'magnitude', 'depth', and 'time' converted successfully.")
            
    except Exception as e:
        print(f"❌ Error in Task 6: {e}")


def task7_extract_month():
    """
    تسک ۷: ایجاد ستون جدید month و استخراج شماره ماه از ستون time
    """
    print("\n" + "="*50)
    print("📅 Task 7: Extracting Month from Time")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. ایجاد ستون month از نوع عدد صحیح (اگر از قبل وجود نداشته باشد)
            add_col_query = """
                ALTER TABLE earthquakes 
                ADD COLUMN IF NOT EXISTS month INTEGER;
            """
            cur.execute(add_col_query)
            
            # ۲. استخراج ماه از ستون time و ذخیره آن در ستون month
            update_query = """
                UPDATE earthquakes
                SET month = EXTRACT(MONTH FROM time);
            """
            cur.execute(update_query)
            updated_rows = cur.rowcount
            print(f"✅ Column 'month' created and populated successfully for {updated_rows} rows.")
            
    except Exception as e:
        print(f"❌ Error in Task 7: {e}")
        
        
def task8_categorize_magnitude():
    """
    تسک ۸: ایجاد ستون category و دسته‌بندی شدت زلزله بر اساس بزرگی (magnitude)
    """
    print("\n" + "="*50)
    print("🏷️ Task 8: Categorizing Earthquake Magnitudes")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. اضافه کردن ستون category
            add_col_query = """
                ALTER TABLE earthquakes 
                ADD COLUMN IF NOT EXISTS category VARCHAR(50);
            """
            cur.execute(add_col_query)
            
            # ۲. به‌روزرسانی ستون با استفاده از شروط (CASE WHEN)
            update_query = """
                UPDATE earthquakes
                SET category = CASE
                    WHEN magnitude < 4 THEN 'Weak'
                    WHEN magnitude >= 4 AND magnitude <= 6 THEN 'Moderate'
                    WHEN magnitude > 6 THEN 'Strong'
                END;
            """
            cur.execute(update_query)
            updated_rows = cur.rowcount
            print(f"✅ Column 'category' created and populated for {updated_rows} rows.")
            
    except Exception as e:
        print(f"❌ Error in Task 8: {e}")
        
        
def task9_extract_region():
    """
    تسک ۹: ایجاد ستون region و استخراج نام منطقه از ستون place
    """
    print("\n" + "="*50)
    print("🌍 Task 9: Extracting Region from Place")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. اضافه کردن ستون region (اگر وجود نداشته باشد)
            add_col_query = """
                ALTER TABLE earthquakes 
                ADD COLUMN IF NOT EXISTS region VARCHAR(255);
            """
            cur.execute(add_col_query)
            
            # ۲. استخراج منطقه با استفاده از توابع رشته‌ای PostgreSQL
            # از SPLIT_PART استفاده می‌کنیم تا متن بعد از کاما را بگیریم
            update_query = """
                UPDATE earthquakes
                SET region = CASE
                    WHEN place LIKE '%, %' THEN TRIM(SPLIT_PART(place, ', ', 2))
                    WHEN place LIKE '%,%' THEN TRIM(SPLIT_PART(place, ',', 2))
                    ELSE TRIM(place)
                END;
            """
            cur.execute(update_query)
            updated_rows = cur.rowcount
            print(f"✅ Column 'region' created and populated successfully for {updated_rows} rows.")
            
    except Exception as e:
        print(f"❌ Error in Task 9: {e}")
        
        
def task9_extract_region():
    """
    تسک ۹: ایجاد ستون region و استخراج نام منطقه از ستون place
    """
    print("\n" + "="*50)
    print("🌍 Task 9: Extracting Region from Place")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # ۱. اضافه کردن ستون region (اگر وجود نداشته باشد)
            add_col_query = """
                ALTER TABLE earthquakes 
                ADD COLUMN IF NOT EXISTS region VARCHAR(255);
            """
            cur.execute(add_col_query)
            
            # ۲. استخراج منطقه با استفاده از توابع رشته‌ای PostgreSQL
            # از SPLIT_PART استفاده می‌کنیم تا متن بعد از کاما را بگیریم
            update_query = """
                UPDATE earthquakes
                SET region = CASE
                    WHEN place LIKE '%, %' THEN TRIM(SPLIT_PART(place, ', ', 2))
                    WHEN place LIKE '%,%' THEN TRIM(SPLIT_PART(place, ',', 2))
                    ELSE TRIM(place)
                END;
            """
            cur.execute(update_query)
            updated_rows = cur.rowcount
            print(f"✅ Column 'region' created and populated successfully for {updated_rows} rows.")
            
    except Exception as e:
        print(f"❌ Error in Task 9: {e}")
        
        
def task10_count_by_month():
    """
    تسک ۱۰: محاسبه تعداد زلزله‌های ثبت‌شده به تفکیک ماه
    """
    print("\n" + "="*50)
    print("📈 Task 10: Earthquakes Count by Month")
    print("="*50)
    
    try:
        with db_cursor() as cur:
            # کوئری برای شمارش زلزله‌ها در هر ماه
            query = """
                SELECT month, COUNT(*) as total_count
                FROM earthquakes
                WHERE month IS NOT NULL
                GROUP BY month
                ORDER BY month;
            """
            cur.execute(query)
            results = cur.fetchall()
            
            print("🗓️ Earthquakes recorded per month:")
            for month, count in results:
                print(f"  - Month {month}: {count} earthquakes")
                
    except Exception as e:
        print(f"❌ Error in Task 10: {e}")
        
        
if __name__ == "__main__":
    print("Starting Data Cleaning and Preprocessing...")
    
    task3_report_table_structure()
    task4_handle_null_values()
    task5_remove_duplicates()
    task6_convert_data_types()
    task7_extract_month()
    task8_categorize_magnitude()
    task9_extract_region()
    task10_count_by_month()
    
    print("\n" + "="*50)
    print("✅ All cleaning tasks (3 to 10) completed successfully!")
    print("="*50)