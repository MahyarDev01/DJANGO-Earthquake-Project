import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.append(project_root)

from Src.Database.db_connection import db_cursor



def task11_region_analysis():
    
    print("\n" + "="*60)
    print("🌍 Task 11: Region-Based Earthquake Analysis")
    print("="*60)

    try:     
        with db_cursor() as cur:
           query = '''
                        SELECT
                            region,
                            COUNT (*) AS total_earthquakes,
                            ROUND(AVG(magnitude):: numeric, 2) AS avg_magnitude,
                            ROUND(AVG(depth):: numeric, 2) AS avg_depth,
                            MIN(magnitude) AS min_magnitude,
                            MAX(magnitude) AS max_magnitude,
                            MIN(depth) AS min_depth,
                            MAX(depth) AS max_depth
                        FROM earthquakes 
                        WHERE region IS NOT NULL   
                        GROUP BY region
                        ORDER BY total_earthquakes DESC; 
            '''
           cur.execute(query)
           results = cur.fetchall()
           print("📊 Earthquake statistics by region:\n")
           for row in results:
                print(f"  region : {row[0]}")
                print(f"  -Total earthquakes : {row[1]}")
                print(f"  - Avg Magnitude     : {row[2]}")
                print(f"  - Avg Depth         : {row[3]}")
                print(f"  - Min Magnitude     : {row[4]}")
                print(f"  - Max Magnitude     : {row[5]}")
                print(f"  - Min Depth         : {row[6]}")
                print(f"  - Max Depth         : {row[7]}")
                print("-" * 40)

        return results
    
    except Exception as e:
        print(f"❌ Error in Task 11: {e}")
        raise

def task12_region_month_category_analysis():

    print("\n" + "="*60)
    print("📅 Task 12: Analysis by Region, Month, and Category")
    print("="*60)

    try:     
        with db_cursor() as cur:
            query = '''
                SELECT region,month,category,
                    COUNT (*) AS total_earthquakes,
                    ROUND(AVG(magnitude) :: numeric, 2) AS avg_magnitude,
                    ROUND(AVG(depth):: numeric, 2) AS avg_depth
                FROM earthquakes
                WHERE region IS NOT NULL
                    AND month IS NOT NULL
                    AND category IS NOT NULL
                GROUP BY region,month,category
                ORDER BY region,month,category;
            '''
            cur.execute(query)
            results = cur.fetchall()

            print("📊 Grouped earthquake analysis:\n")
            for row in results:
                print(f"Region: {row[0]} | Month: {row[1]} | Category: {row[2]}")
                print(f"  - Total Earthquakes : {row[3]}")
                print(f"  - Avg Magnitude     : {row[4]}")
                print(f"  - Avg Depth         : {row[5]}")
                print("-" * 50)

        return results
    
    except Exception as e:
        print(f'❌ Error in task 12 : {e}' )
        raise

    
def task13_top_10_recent_strong_earthquakes():

    print("\n" + "=" * 60)
    print("⚡ Task 13: Top 10 Recent Strong Earthquakes")
    print("=" * 60)

    try:     
        with db_cursor() as cur:
            query = '''
                SELECT  id,
                        time,
                        place,
                        region,
                        magnitude,
                        depth,
                        source
                FROM earthquakes
                WHERE magnitude > 6
                ORDER BY time DESC , magnitude DESC
                LIMIT 10;
            '''
            cur.execute(query)
            results = cur.fetchall() 

            print("🕒 10 recent strong earthquakes:\n")
            for row in results:
                print(f"  ID                : {row[0]}")
                print(f"  Time              : {row[1]}")
                print(f"  Place             : {row[2]}")
                print(f"  Region            : {row[3]}")
                print(f"  Magnitude         : {row[4]}")
                print(f"  Depth             : {row[5]}")
                print(f"  Source            : {row[6]}")
                print("-" * 40)
            return results 
             
    except Exception as e:
        print(f'❌ Error in Task 13: {e}')
        raise


def task14_dangerous_earthquakes():

    
    print("\n" + "=" * 60)
    print("🌋 Task 14: Strong and Shallow Earthquakes")
    print("=" * 60)

    try:     
        with db_cursor() as cur:
            query = '''
                SELECT id,
                    time,
                    place,
                    region,
                    magnitude,
                    depth,
                    source
                FROM earthquakes
                WHERE magnitude > 6 
                    AND depth < 50
                ORDER BY magnitude DESC , time DESC;
            '''

            cur.execute(query)
            results = cur.fetchall()
            print("📌 Earthquakes with magnitude > 6 and depth < 50 km:\n")

            for row in results:
                print(f"  ID                : {row[0]}")
                print(f"  Time              : {row[1]}")
                print(f"  Place             : {row[2]}")
                print(f"  Region            : {row[3]}")
                print(f"  Magnitude         : {row[4]}")
                print(f"  Depth             : {row[5]}")
                print(f"  Source            : {row[6]}")
                print("-" * 40)

            return results
    
    except Exception as e:
        print(f'❌ Error in Task 14: {e}')
        raise


def task15_earthquake_count_by_source():

    # تعداد زلزله های ثبت شده برای هر منبع داده

    print("\n" + "=" * 60)
    print("🛰️ Task 15: Earthquake Count by Source")
    print("=" * 60)

    try:     
        with db_cursor() as cur:
            query = '''
                    SELECT source,
                        COUNT (*) AS total_earthquakes
                    FROM earthquakes
                    GROUP BY source
                    ORDER BY total_earthquakes DESC;     
            '''

            cur.execute(query)
            results = cur.fetchall()

            print("📊 Earthquake count by source:\n")
            for row in results:
                print(f" Source: {row[0]} | Count: {row[1]}")

            return results 

    except Exception as e:
        print(f'❌ Error in Task 15: {e}')
        raise


def task16_average_magnitude_by_region_source():


    print("\n" + "=" * 60)
    print("📈 Task 16: Average Magnitude by Region and Source")
    print("=" * 60)

    try:     
        with db_cursor() as cur:
            query = '''
                SELECT region,
                source,
                ROUND(AVG(magnitude):: numeric,2) AS avg_magnitude
                FROM earthquakes
                WHERE region IS NOT NULL
                    AND source IS NOT NULL
                GROUP BY source, region
                ORDER BY avg_magnitude DESC;
            '''

            cur.execute(query)
            results = cur.fetchall()
            
        
            print("📊 Average magnitude by region and source:\n")
            for row in results:
                print(f"  Region        : {row[0]}")
                print(f"  Source        : {row[1]}")
                print(f"  Avg Magnitude : {row[2]}")
                print("-" * 40)

            return results
    
    except Exception as e:
        print(F'❌ Error in Task 16: {e}')
        raise        



def task17_create_indexes():

    print("\n" + "=" * 60)
    print("⚙️ Task 17: Creating Indexes")
    print("=" * 60)

    try:     
        with db_cursor() as cur:
            cur.execute ('''
                            CREATE INDEX IF NOT EXISTS idx_earthquakes_time
                            ON earthquakes(time);
            ''')
            cur.execute ( '''
                            CREATE INDEX IF NOT EXISTS idx_earthquakes_magnitude
                            ON earthquakes(magnitude);
                            ''')
            cur.execute ( '''
                            CREATE INDEX IF NOT EXISTS idx_earthquakes_region
                            ON earthquakes(region);
                        ''')
            cur.execute ('''
                        SELECT indexname
                        FROM pg_indexes
                        WHERE tablename = 'earthquakes'
                            AND indexname IN('idx_earthquakes_time',
                              'idx_earthquakes_magnitude',
                              'idx_earthquakes_region')
                        ORDER BY indexname;
            ''')

            rows = cur.fetchall()

            index_names = [row[0] for row in rows]

            print("✅ Indexes checked/created successfully:")
            for index_name in index_names:
                print(f' -{index_name}')

            return index_names
    except Exception as e:
        print(f'❌ Error in task 17: {e}')
        raise


if __name__ == "__main__":
    print("Starting SQL Analysis Tasks (11 to 17)...")

    task11_results = task11_region_analysis()
    task12_results = task12_region_month_category_analysis()
    task13_results = task13_top_10_recent_strong_earthquakes()
    task14_results = task14_dangerous_earthquakes()
    task15_results = task15_earthquake_count_by_source()
    task16_results = task16_average_magnitude_by_region_source()
    task17_results = task17_create_indexes()


    print("\n" + "=" * 60)
    print("✅ All analysis tasks (11 to 17) completed successfully!")
    print("=" * 60)
