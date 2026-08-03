import os
import sys
import time
import logging

# تنظیم مسیر برای دسترسی به تمام ماژول‌ها
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# ==========================================
# تنظیمات حرفه‌ای Logging (ذخیره در فایل و نمایش در کنسول)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# ==========================================
# ایمپورت کردن تمام ماژول‌های پروژه
# ==========================================
try:
    # Phase 1: Data Collection
    from Src.Data_collection import usgs_api, emsc_scraping, geofon_scraping
    from Src.Analysis import clean_data
    
    # Phase 2 & 3: Database & Load
    from Src.Database import db_connection, db_tables, csv_to_db
    
    # Phase 4 & 5: Transform & Analysis (SQL)
    from Src.Analysis import clean_sql, sql_query
    
    # Phase 6: Charts
    from Src.Charts import heatmap, histogram, linechart, scatter, boxplot
        
except Exception as e:
    logging.critical(f"❌ Error importing modules: {e}")
    sys.exit(1)


def run_pipeline():
    logging.info("🚀 Starting the Earthquake ELT Pipeline...")
    start_time = time.time()

    try:
        # ---------------------------------------------------------
        # فاز ۱: استخراج داده‌ها (Extract)
        # ---------------------------------------------------------
        logging.info("--- PHASE 1: Data Collection (Scraping & API) ---")
        
        logging.info("Starting USGS API download...")
        usgs_api.collect_usgs_data()
        
        logging.info("Starting EMSC Scraping...")
        emsc_scraping.emsc_japan_lastmonth()
        
        logging.info("Starting GEOFON Scraping...")
        geofon_scraping.geofon_japan_lastmonth()
        
        logging.info("Cleaning raw Kaggle dataset...")
        clean_data.save_cleaned_dataset()
        
        logging.info("✅ Phase 1 Completed Successfully.")

        # ---------------------------------------------------------
        # فاز ۲: راه‌اندازی پایگاه داده (Setup DB)
        # ---------------------------------------------------------
        logging.info("--- PHASE 2: Database Setup ---")
        db_connection.create_database_if_not_exists()
        db_tables.create_tables()
        logging.info("✅ Phase 2 Completed Successfully.")

        # ---------------------------------------------------------
        # فاز ۳: بارگذاری داده‌ها در دیتابیس (Load)
        # ---------------------------------------------------------
        logging.info("--- PHASE 3: Loading Data to Database ---")
        csv_to_db.import_data_to_db()
        logging.info("✅ Phase 3 Completed Successfully.")

        # ---------------------------------------------------------
        # فاز ۴: پاکسازی داخل دیتابیس (Transform)
        # ---------------------------------------------------------
        logging.info("--- PHASE 4: SQL Data Cleaning ---")
        clean_sql.task3_report_table_structure()
        clean_sql.task4_handle_null_values()
        clean_sql.task5_remove_duplicates()
        clean_sql.task6_convert_data_types()
        clean_sql.task7_extract_month()
        clean_sql.task8_categorize_magnitude()
        clean_sql.task9_extract_region()
        clean_sql.task10_count_by_month()
        logging.info("✅ Phase 4 Completed Successfully.")

        # ---------------------------------------------------------
        # فاز ۵: تحلیل داده‌ها و ایندکس‌گذاری (Analysis)
        # ---------------------------------------------------------
        logging.info("--- PHASE 5: SQL Analysis & Indexing ---")
        sql_query.task11_region_analysis()
        sql_query.task12_region_month_category_analysis()
        sql_query.task13_top_10_recent_strong_earthquakes()
        sql_query.task14_dangerous_earthquakes()
        sql_query.task15_earthquake_count_by_source()
        sql_query.task16_average_magnitude_by_region_source()
        sql_query.task17_create_indexes()
        logging.info("✅ Phase 5 Completed Successfully.")

        # ---------------------------------------------------------
        # فاز ۶: رسم نمودارها (Visualization)
        # ---------------------------------------------------------
        logging.info("--- PHASE 6: Generating Charts ---")
        heatmap.plot_heatmap()
        histogram.plot_magnitude_histogram()
        linechart.plot_line_chart()
        scatter.plot_scatter()
        boxplot.plot_boxplot()
        logging.info("✅ Phase 6 Completed Successfully.")

        # ---------------------------------------------------------
        # پایان پایپ‌لاین
        # ---------------------------------------------------------
        end_time = time.time()
        elapsed_time = round((end_time - start_time) / 60, 2)
        logging.info(f"🎉 All pipeline steps executed successfully in {elapsed_time} minutes!")

    except Exception as e:
        logging.error(f"❌ PIPELINE FAILED! Error details: {e}")
        # با استفاده از raise ارور رو کامل نشون می‌دیم تا بشه دیباگ کرد
        raise

if __name__ == "__main__":
    run_pipeline()