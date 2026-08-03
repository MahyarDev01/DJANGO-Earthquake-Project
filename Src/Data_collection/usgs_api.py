import requests
from datetime import datetime, timedelta
from configs import JAPAN_USGS_CSV


    
def build_params():

    end_date = datetime.today().date()
    start_date = end_date - timedelta(days=30)

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
    return params

def download_usgs_data(params):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response 

def save_csv(response, file_path):

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(response.text)


def collect_usgs_data():
        params = build_params()
        response = download_usgs_data(params)
        save_csv(response, JAPAN_USGS_CSV)
        print(" USGS Done! ")

if __name__ == '__main__':
     collect_usgs_data()