import requests
from datetime import datetime, timedelta
import csv
from io import StringIO

end_date = datetime.today().date()
start_date = end_date - timedelta(days=30)

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

params = {
    "format": "csv",
    "starttime": str(start_date),
    "endtime": str(end_date),
    "minlatitude": 24,
    "maxlatitude": 46,
    "minlongitude": 123,
    "maxlongitude": 146,
    "minmagnitude": 1
}

response = requests.get(url, params=params)

# بهتر است وضعیت درخواست بررسی شود
response.raise_for_status()

# --------------------------------------------------
# نسخه قدیمی:
#
# با این روش اول خروجی API داخل یک فایل موقت ذخیره می‌شد
# و  دوباره همان فایل خونده می‌شد
#
# with open("japan_earthquakes.csv", "w", encoding="utf-8") as f:
#     f.write(response.text)
#
# earthquake = []
#
# with open("japan_earthquakes.csv", "r", encoding="utf-8") as f:
#
#     data = csv.DictReader(f)
#
#     dictrow = {}
#
#     for row in data:
#         dictrow['time'] = row['time']
#         dictrow['latitude'] = row['latitude']
#         dictrow['longitude'] = row['longitude']
#         dictrow['place'] = row['place']
#         dictrow['mag'] = row['mag']
#         dictrow['depth'] = row['depth']
#         dictrow['magSource'] = row['magSource']
#
#         earthquake.append(dictrow)
#
# مشکل اول:
# فایل موقت غیرضروری ساخته میشد و نیازی نبود بهش
#
# مشکل دوم:
# فقط یک dict ساخته شده بود و همه رکوردها
# به همان دیکشنری اشاره می‌کردند

# به زبانی میشه گفت تمام ردیف ها تکراری بودن
# --------------------------------------------------

earthquake = []

# مستقیماً CSV دریافتی از API خوانده می‌شود
data = csv.DictReader(StringIO(response.text))

for row in data:

    dictrow = {
        'time': row['time'],
        'latitude': row['latitude'],
        'longitude': row['longitude'],
        'place': row['place'],
        'mag': row['mag'],
        'depth': row['depth'],
        'magSource': row['magSource']
    }

    earthquake.append(dictrow)

# داخل پوشه ی مربوط به دیتا سیو بشه فایل CSV 
with open('./Data/CSV/JAPAN_USGS.csv', 'w', newline='', encoding='utf-8') as f:

    headers = [
        'time',
        'latitude',
        'longitude',
        'place',
        'mag',
        'depth',
        'magSource'
    ]

    writer = csv.DictWriter(f, fieldnames=headers)

    writer.writeheader()
    writer.writerows(earthquake)

print(f"Saved {len(earthquake)} earthquakes to JAPAN_USGS.csv")