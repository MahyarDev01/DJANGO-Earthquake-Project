import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "Data")
CSV_DIR = os.path.join(DATA_DIR, "CSV")


# Specific files
JAPAN_EMSC_CSV = os.path.join(CSV_DIR, "JAPAN_EMSC.csv")
JAPAN_DATASET_CSV = os.path.join(CSV_DIR, "JAPAN_DATASET.csv")
JAPAN_GEOFON_CSV = os.path.join(CSV_DIR, "JAPAN_GEOFON.csv")
JAPAN_USGS_CSV = os.path.join(CSV_DIR, "JAPAN_USGS.csv")