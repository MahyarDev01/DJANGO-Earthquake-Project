# 🌏 پروژه تحلیل داده‌های زلزله ژاپن

## معرفی پروژه

این پروژه با هدف جمع‌آوری، پاک‌سازی، ذخیره‌سازی و تحلیل داده‌های مربوط به زلزله‌های کشور ژاپن انجام می‌شود.

داده‌ها از ۴ منبع جمع‌آوری می‌شوند:

- **USGS** (از طریق API)
- **GEOFON** (Web Scraping با BeautifulSoup)
- **EMSC** (Dynamic Scraping با Selenium)
- **Dataset** آماده‌ی ارائه‌شده برای پروژه (`JAPAN_DATASET.csv`)

و پس از پاک‌سازی و ذخیره‌سازی در PostgreSQL، تحلیل‌های آماری و نمودارهای مختلف روی آن‌ها انجام می‌شود.

---

## روند کلی اجرای پروژه (فازهای `main.py`)

```
Phase 1: Data Collection & Cleaning
   (usgs_api, geofon_scraping, emsc_scraping + clean_data.py)
        ↓
Phase 2: Database Setup
   (db_connection, db_tables)
        ↓
Phase 3: Load CSVs into Database
   (csv_to_db)
        ↓
Phase 4: SQL Cleaning  (clean_sql.py — tasks 3 to 10)
        ↓
Phase 5: SQL Analysis & Indexing  (sql_query.py — tasks 11 to 17)
        ↓
Phase 6: Chart Generation  (Src/Charts)
```

اجرای کل پایپ‌لاین از ریشه‌ی پروژه:

```bash
python main.py
```

هر مرحله هم زمان‌بندی‌شده و هم لاگ می‌شود (کنسول + فایل `pipeline.log`)، و در صورت بروز خطا در هر فاز، پایپ‌لاین متوقف شده و خطا را کامل نشان می‌دهد.

---

# 📁 ساختار کلی پروژه

```
DJANGO-Earthquake-Project/
├── README.md
├── requirements.txt
├── .env                  # DB_PASSWORD (ساخته می‌شود، در گیت قرار نمی‌گیرد)
├── .gitignore
├── configs.py
├── main.py
├── pipeline.log           # خروجی اجرای main.py

├── Data/
│   ├── CSV/
│   └── *.png              # خروجی نمودارها

├── Src/
│   ├── Data_collection/
│   ├── Analysis/
│   ├── Database/
│   ├── Charts/
│   └── Other/

├── SQL/

└── Tests/
```

---

# 📄 فایل‌های ریشه‌ی پروژه

## configs.py

مسیرهای مورد استفاده در کل پروژه را یک‌جا تعریف می‌کند تا بقیه‌ی ماژول‌ها به‌جای مسیر خام از این ثابت‌ها استفاده کنند:

- `DATA_DIR`, `CSV_DIR`
- `RAW_JAPAN_DATASET_CSV`, `JAPAN_DATASET_CSV`
- `JAPAN_USGS_CSV`, `JAPAN_GEOFON_CSV`, `JAPAN_EMSC_CSV`
- `FIREFOX_BINARY` (برای Selenium در `emsc_scraping.py`)

## .env

فایل محیطی (خارج از گیت) که `DB_PASSWORD` را نگه می‌دارد و توسط `python-decouple` در `db_connection.py` خوانده می‌شود. قبل از اجرای پروژه باید در ریشه ساخته شود:

```
DB_PASSWORD=your_password
```

## main.py

نقطه‌ی ورود پروژه. تمام ۶ فاز بالا را به‌ترتیب و با `logging` (به‌جای `print`) اجرا می‌کند و مدت زمان کل اجرا را در انتها گزارش می‌دهد.

## requirements.txt

کتابخانه‌های مورد نیاز پروژه (نسخه‌بندی‌شده)، از جمله: `pandas`, `psycopg2-binary`, `SQLAlchemy`, `matplotlib`, `seaborn`, `requests`, `beautifulsoup4`, `selenium`, `python-decouple`.

---

# 🗂️ Data/

## Data/CSV/

داده‌های خام و نیمه‌پردازش‌شده:

| فایل | توضیح |
|---|---|
| `JAPAN_USGS.csv` | خروجی خام API سایت USGS |
| `JAPAN_GEOFON.csv` | خروجی خام Web Scraping سایت GEOFON |
| `JAPAN_EMSC.csv` | خروجی خام Selenium Scraping سایت EMSC |
| `Raw_JAPAN_DATASET.csv` | دیتاست آماده‌ی خام ارائه‌شده برای پروژه |
| `JAPAN_DATASET.csv` | خروجی پاک‌سازی‌شده‌ی `Raw_JAPAN_DATASET.csv` توسط `clean_data.py` (پاندا) |

هر ۴ فایل (`USGS`, `GEOFON`, `EMSC`, `DATASET`) در نهایت توسط `csv_to_db.py` با ستون `source` مشخص و در جدول `earthquakes` بارگذاری می‌شوند.

## Data/*.png

خروجی نمودارهای `Src/Charts` مستقیماً در همین پوشه ذخیره می‌شوند (پوشه‌ی جداگانه‌ی `Results/` در نسخه‌ی فعلی وجود ندارد):

- `histogram_magnitude.png`
- `linechart_trend.png`
- `scatter_magnitude.png`
- `boxplot_depth_mag.png`
- `heatmap_earthquakes.png`

---

# 💻 Src/

## 🌐 Src/Data_collection/

مسئول جمع‌آوری داده از منابع مختلف.

| فایل | مسئولیت | مباحث |
|---|---|---|
| `usgs_api.py` | ساخت پارامترها و دریافت داده از USGS API | API, Requests |
| `geofon_scraping.py` | استخراج جدول زلزله‌ها از سایت GEOFON | Web Scraping, BeautifulSoup |
| `emsc_scraping.py` | کنترل مرورگر Firefox و استخراج داده‌ی داینامیک از EMSC | Selenium |

## 🧹📊 Src/Analysis/

پاک‌سازی و تحلیل داده‌ها؛ بین سه فایل به این شکل تقسیم شده:

### clean_data.py

پاک‌سازی سطح پاندا (پیش از ورود به دیتابیس)، فقط روی `Raw_JAPAN_DATASET.csv`:

- `parse_magnitude` / `parse_depth` / `parse_coordinate` / `parse_time` / `clean_place`: استانداردسازی مقادیر متنیِ نامنظم (اعداد نوشته‌شده به حروف، واحدهای مختلف عمق، فرمت‌های مختلف تاریخ و ...)
- `clean_dataset` / `save_cleaned_dataset`: خروجی نهایی را در `JAPAN_DATASET.csv` ذخیره می‌کند

هیچ ردیفی در این مرحله حذف نمی‌شود؛ مقادیر غیرقابل‌تفسیر فقط `None`/`NaN` می‌شوند. حذف رکورد کار مرحله‌ی SQL است.

### clean_sql.py  (تسک‌های ۳ تا ۱۰ — پاک‌سازی سمت دیتابیس)

| تابع | کار |
|---|---|
| `task3_report_table_structure` | گزارش ستون‌ها، نوع داده‌ها و تعداد رکوردهای جدول |
| `task4_handle_null_values` | شمارش و حذف رکوردهای دارای مقدار خالی/NULL در فیلدهای اصلی؛ پرکردن `place` خالی با `'Unknown'` |
| `task5_remove_duplicates` | حذف رکوردهای تکراری بر اساس `time`, `latitude`, `longitude` |
| `task6_convert_data_types` | پاک‌سازی رشته‌های نامعتبر با Regex و تبدیل نوع ستون‌های `magnitude`, `depth` به `FLOAT` و `time` به `TIMESTAMP` |
| `task7_extract_month` | ساخت ستون `month` از `time` |
| `task8_categorize_magnitude` | ساخت ستون `category` (Weak / Moderate / Strong) بر اساس `magnitude` |
| `task9_extract_region` | ساخت ستون `region` با استخراج از `place` |
| `task10_count_by_month` | گزارش تعداد زلزله‌ها به تفکیک ماه |

### sql_query.py  (تسک‌های ۱۱ تا ۱۷ — تحلیل و ایندکس‌گذاری)

| تابع | کار |
|---|---|
| `task11_region_analysis` | تعداد، میانگین/کمینه/بیشینه‌ی magnitude و depth به تفکیک `region` |
| `task12_region_month_category_analysis` | همان آمار به تفکیک `region`, `month`, `category` |
| `task13_top_10_recent_strong_earthquakes` | ۱۰ زلزله‌ی اخیر با magnitude بیشتر از ۶ |
| `task14_dangerous_earthquakes` | زلزله‌های با magnitude بیشتر از ۶ و depth کمتر از ۵۰ کیلومتر |
| `task15_earthquake_count_by_source` | تعداد زلزله به تفکیک منبع داده (`source`) |
| `task16_average_magnitude_by_region_source` | میانگین magnitude به تفکیک `region` و `source` |
| `task17_create_indexes` | ساخت ایندکس روی `time`, `magnitude`, `region` |

هر تابع لیستی از tuple (خروجی خام `cursor.fetchall()`) برمی‌گرداند، نه DataFrame.

> **نکته:** `task4` و `task6` استثناهای داخلی‌شان را فقط چاپ می‌کنند و دوباره raise نمی‌کنند، و کوئری‌های `task6` فرض می‌کنند ستون‌ها هنوز متنی‌اند. بنابراین این پایپ‌لاین باید هربار روی یک جدول تازه‌بارگذاری‌شده (raw) اجرا شود، نه روی جدولی که قبلاً یک‌بار پردازش شده.

## 🗄️ Src/Database/

مدیریت ارتباط پروژه با PostgreSQL.

| فایل | کار |
|---|---|
| `db_connection.py` | `create_database_if_not_exists`, `get_connection`, `get_engine` (SQLAlchemy) و context manager `db_cursor` که commit/rollback را خودکار مدیریت می‌کند |
| `db_tables.py` | ساخت (و بازساخت) جدول `earthquakes` با ستون‌های خام `VARCHAR` |
| `csv_to_db.py` | خواندن هر ۴ فایل CSV، یکسان‌سازی نام ستون‌ها (`date→time`, `region→place`, `mag→magnitude`)، افزودن ستون `source` و درج در جدول `earthquakes` |

## 📈 Src/Charts/

نمایش تصویری نتایج تحلیل (Matplotlib + Seaborn)، هر نمودار مستقیماً از دیتابیس می‌خواند و در `Data/` ذخیره می‌کند:

| فایل | تابع | نمودار |
|---|---|---|
| `histogram.py` | `plot_magnitude_histogram` | توزیع magnitude به تفکیک source و ۵ منطقه‌ی برتر |
| `linechart.py` | `plot_line_chart` | روند روزانه‌ی تعداد و میانگین magnitude زلزله‌ها |
| `scatter.py` | `plot_scatter` | رابطه‌ی magnitude با depth و با زمان |
| `boxplot.py` | `plot_boxplot` | توزیع magnitude در دسته‌های عمق (Shallow/Intermediate/Deep/Very Deep) |
| `heatmap.py` | `plot_heatmap` | تراکم جغرافیایی زلزله‌ها و رابطه‌ی فاصله تا توکیو با magnitude |

## 🛠️ Src/Other/

### helpers_func.py

- `haversine_distance(lat1, lon1, lat2, lon2)`: محاسبه‌ی فاصله‌ی جغرافیایی (کیلومتر) بین دو مختصات؛ در `heatmap.py` برای فاصله تا توکیو استفاده می‌شود.

---

# 🧾 SQL/

## create_schema.sql

اسکیمای مرجع جدول `earthquakes` (همان ستون‌بندی که `db_tables.create_tables()` به‌صورت برنامه‌نویسی‌شده هم می‌سازد؛ برای مستندسازی/اجرای دستی نگه‌داری می‌شود).

---

# ✅ Tests/

تمام تست‌ها با `unittest` نوشته شده‌اند و به یک PostgreSQL در دسترس (طبق `.env`) نیاز دارند — Mock نمی‌شوند.

| فایل | پوشش |
|---|---|
| `test_collectors.py` | `usgs_api` (پارامترها، دانلود، ذخیره‌ی CSV)، `geofon_scraping`، `emsc_scraping` |
| `test_cleaning.py` | توابع `clean_data.py` (parse_magnitude/parse_depth/parse_coordinate/parse_time) و `clean_dataset` |
| `test_database.py` | اتصال به دیتابیس، وجود جدول `earthquakes`، درج داده‌ها |
| `test_analysis.py` | `clean_sql.py` (تسک‌های ۳ تا ۱۰: نوع ستون‌ها، حذف NULL/تکراری، ستون‌های month/category/region) و `sql_query.py` (تسک‌های ۱۱ تا ۱۷: صحت هر کوئری تحلیلی و ساخت ایندکس‌ها) |

اجرای همه‌ی تست‌ها از ریشه‌ی پروژه:

```bash
python -m unittest discover -s Tests
```

---

# 🎯 خلاصه مسئولیت بخش‌ها

| بخش | مسئولیت |
|---|---|
| `Src/Data_collection` | جمع‌آوری داده از USGS / GEOFON / EMSC |
| `Src/Analysis/clean_data.py` | پاک‌سازی سطح پاندا روی دیتاست خام |
| `Src/Database` | ساخت دیتابیس، جدول و بارگذاری داده |
| `Src/Analysis/clean_sql.py` | پاک‌سازی و تبدیل نوع داده‌ها در سطح SQL (تسک ۳-۱۰) |
| `Src/Analysis/sql_query.py` | تحلیل‌های آماری و ایندکس‌گذاری (تسک ۱۱-۱۷) |
| `Src/Charts` | تولید نمودارها |
| `Tests` | تست و اعتبارسنجی هر لایه |
