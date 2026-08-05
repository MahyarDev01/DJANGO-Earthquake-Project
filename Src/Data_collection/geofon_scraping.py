import re
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import time
import requests
import pandas as pd
from configs import JAPAN_GEOFON_CSV

# run it from project root with: python -m Src.Data_collection.geofon_scraping 





def geofon_data_earthquake_scrape(date_start:date, date_end:date, latitude_min:int, latitude_max:int, longitude_min:int, longitude_max:int, magnitude_min:int = 1):

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:

        url = f"https://geofon.gfz.de/eqinfo/list.php?datemin={str(date_start)}&datemax={str(date_end)}&latmax={latitude_max}&lonmin={longitude_min}&lonmax={longitude_max}&latmin={latitude_min}&magmin={magnitude_min}&fmt=html&nmax=1000"

        all_data = []
        post_links = []

        while url:

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            container = soup.find("div", class_="eqlist")
            rows = container.find_all('a')

            for row in rows: # appending post links to post_links list
                link = row.get('href')
                if link and "event.php" in link:
                    post_links.append(link)

            #checking pagination and if there is another page exist to scrape
            earlier_link = container.find('a', string=lambda t: t and "Earlier events" in t)
            if earlier_link and earlier_link.get('href'):
                url = earlier_link.get('href')
            else:
                url = None   

            for link in post_links: # getting data from post pages
                time.sleep(0.5)
                response = requests.get(link, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                data = {}
                event_table = soup.find("table", class_="table-condensed")
                for row in event_table.find_all("tr"):
                    label_cell = row.find("td", class_="dt-like")
                    if not label_cell:
                        continue
                    label = label_cell.get_text(strip=True)
                    value_cell = label_cell.find_next_sibling("td")
                    if value_cell:
                        data[label] = value_cell.get_text(strip=True)

                raw_epicenter = data["Epicenter"]
                match_mag = re.search(r"([\d.]+)°([EW])\s*([\d.]+)°([NS])", raw_epicenter)
                if match_mag:
                    lon_val, lon_dir, lat_val, lat_dir = match_mag.groups()
                    lon_val = float(lon_val) * (-1 if lon_dir == "W" else 1)
                    lat_val = float(lat_val) * (-1 if lat_dir == "S" else 1)
                else:
                    lon_val, lat_val = None, None

                #pull date and time from the "Time" field
                raw_time = data["Time"]
                match_time = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", raw_time)
                date_time = match_time.group() if match_time else None
                region_val = data["F-E Region"]
                raw_depth = data["Depth"]
                depth_val = re.search(r'\d+', raw_depth).group()
                raw_magnitude = data["Magnitude"]
                match_mag = re.search(r"([\d.]+)\s*\(([^)]+)\)", raw_magnitude)
                mag_val = float(match_mag.group(1))
                mgtype_val = match_mag.group(2)

                all_data.append({
                                    "date": date_time,
                                    "latitude": lat_val,
                                    "longitude": lon_val,
                                    "depth": depth_val,
                                    "magnitude": mag_val,
                                    "magtype": mgtype_val,
                                    "region": region_val
                                })

            
            df = pd.DataFrame(all_data)
            df.to_csv(JAPAN_GEOFON_CSV, index=False, encoding="utf-8-sig")

            return True

    except requests.exceptions.HTTPError as err:
        print('HTTP Error')
        print(err.args[0])
        return False

    except:
        print('an error ocurred, Try again...')
        return False

def geofon_japan_lastmonth():
    end_date = datetime.today().date() 
    start_date = end_date - timedelta(days=30)

    return geofon_data_earthquake_scrape(start_date, end_date, 24, 46, 123, 146, 1)



if __name__ == '__main__':

    if geofon_japan_lastmonth():
        
        print("DONE!")



    
