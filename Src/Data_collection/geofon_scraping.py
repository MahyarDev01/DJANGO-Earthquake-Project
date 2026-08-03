import re
from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import time
import requests
import pandas as pd
from configs import JAPAN_GEOFON_CSV


def geofon_data_earthquake_scrape(date_start:date, date_end:date, latitude_min:int, latitude_max:int, longitude_min:int, longitude_max:int, magnitude_min:int = 1):

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        url = f"https://geofon.gfz.de/eqinfo/list.php?datemin={str(date_start)}&datemax={str(date_end)}&latmax={latitude_max}&lonmin={longitude_min}&lonmax={longitude_max}&latmin={latitude_min}&magmin={magnitude_min}&fmt=html&nmax=1000"

        all_data = []
        
        while url:
            print(f"📡 Scrapping page: {url}")
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            container = soup.find("div", class_="eqlist")
            if not container:
                container = soup.find("table") 
                
            if not container:
                print("⚠️ Could not find earthquake table on GEOFON.")
                break

            post_links = []
            rows = container.find_all('a')

            for row in rows: 
                link = row.get('href')
                if link and "event.php" in link:
                    if not link.startswith("http"):
                        link = "https://geofon.gfz.de/eqinfo/" + link.split("/")[-1]
                    post_links.append(link)

            earlier_link = container.find('a', string=lambda t: t and "Earlier events" in t)
            if earlier_link and earlier_link.get('href'):
                url = earlier_link.get('href')
                if not url.startswith("http"):
                    url = "https://geofon.gfz.de/eqinfo/" + url.split("/")[-1]
            else:
                url = None   

            for link in post_links: 
                time.sleep(0.5)
                try:
                    response = requests.get(link, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    data = {}
                    event_table = soup.find("table", class_="table-condensed")
                    if not event_table:
                        continue
                        
                    for row in event_table.find_all("tr"):
                        label_cell = row.find("td", class_="dt-like")
                        if not label_cell:
                            continue
                        label = label_cell.get_text(strip=True)
                        value_cell = label_cell.find_next_sibling("td")
                        if value_cell:
                            data[label] = value_cell.get_text(strip=True)

                    raw_epicenter = data.get("Epicenter", "")
                    match_mag = re.search(r"([\d.]+)°([EW])\s*([\d.]+)°([NS])", raw_epicenter)
                    if match_mag:
                        lon_val, lon_dir, lat_val, lat_dir = match_mag.groups()
                        lon_val = float(lon_val) * (-1 if lon_dir == "W" else 1)
                        lat_val = float(lat_val) * (-1 if lat_dir == "S" else 1)
                    else:
                        lon_val, lat_val = None, None

                    raw_time = data.get("Time", "")
                    match_time = re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+", raw_time)
                    date_time = match_time.group() if match_time else None
                    
                    region_val = data.get("F-E Region", "Unknown")
                    
                    raw_depth = data.get("Depth", "0")
                    depth_match = re.search(r'\d+', raw_depth)
                    depth_val = depth_match.group() if depth_match else None
                    
                    raw_magnitude = data.get("Magnitude", "")
                    match_mag = re.search(r"([\d.]+)\s*\(([^)]+)\)", raw_magnitude)
                    if match_mag:
                        mag_val = float(match_mag.group(1))
                        mgtype_val = match_mag.group(2)
                    else:
                        mag_val, mgtype_val = None, None

                    all_data.append({
                        "date": date_time,
                        "latitude": lat_val,
                        "longitude": lon_val,
                        "depth": depth_val,
                        "magnitude": mag_val,
                        "magtype": mgtype_val,
                        "region": region_val
                    })
                except Exception as inner_e:
                    print(f"⚠️ Error parsing single event {link}: {inner_e}")

        if all_data:
            df = pd.DataFrame(all_data)
            df.to_csv(JAPAN_GEOFON_CSV, index=False, encoding="utf-8-sig")
            print(f"✅ Downloaded {len(df)} records from GEOFON.")
            return True
        else:
            print("⚠️ No data found for the given criteria.")
            df = pd.DataFrame(columns=["date", "latitude", "longitude", "depth", "magnitude", "magtype", "region"])
            df.to_csv(JAPAN_GEOFON_CSV, index=False, encoding="utf-8-sig")
            return True

    except Exception as e:
        print(f'❌ An error ocurred in GEOFON scraper: {e}')
        import traceback
        traceback.print_exc()
        return False

def geofon_japan_lastmonth():
    end_date = datetime.today().date() 
    start_date = end_date - timedelta(days=30)

    return geofon_data_earthquake_scrape(start_date, end_date, 24, 46, 123, 146, 1)


if __name__ == '__main__':
    if geofon_japan_lastmonth():
        print("DONE!")