import requests
from datetime import datetime, timedelta

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
response.raise_for_status()

file_path = './Data/CSV/JAPAN_USGS.csv'

with open(file_path, "w", encoding="utf-8") as f:
    f.write(response.text)

print("USGS Done !!")
