import requests
from bs4 import BeautifulSoup

import pandas as pd


# import numpy as np
#-------------------------//-------------------------------

# page url for earthquake data
url = "https://geofon.gfz.de/eqinfo/form.php"

page = requests.get(url)


#  html parser
soup = BeautifulSoup(page.text, "html.parser")

tables = soup.find_all("table")

print(tables)

# save as csv file
df = pd.read_html(str(tables))[0]
df.to_csv("Data/CSV/JAPAN_GEOFON.csv", index=False)