import requests
from datetime import datetime, timedelta 
import csv
  
end_date = datetime.today().date() 
start_date = end_date - timedelta(days=30)  
url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

params = { "format": "csv",
    "starttime": str(start_date),     
    "endtime": str(end_date),    
    "minlatitude": 24,     
    "maxlatitude": 46,     
    "minlongitude": 123,     
    "maxlongitude": 146,     
    "minmagnitude": 1 }
  
response = requests.get(url, params=params)
  
with open("japan_earthquakes.csv", "w", encoding="utf-8") as f:
        f.write(response.text)

earthquake =[]
with open("japan_earthquakes.csv", "r", encoding="utf-8") as f:
        
        data =csv.DictReader(f)
        dictrow = {}
        for row in data:
                dictrow['time'] = row['time']
                dictrow['latitude'] = row['latitude']
                dictrow['longitude'] = row['longitude']
                dictrow['place'] = row['place']
                dictrow['mag'] = row['mag']
                dictrow['depth'] = row['depth']
                dictrow['magSource'] = row['magSource'] 

                earthquake.append(dictrow)
            
with open('JAPAN_USGS.csv', 'w', encoding='utf-8') as f:
        
        headers = ['time', 'latitude', 'longitude', 'place', 'mag', 'depth', 'magSource']
        writer = csv.DictWriter(f, fieldnames = headers)
        
        writer.writeheader()
        writer.writerows(earthquake)



