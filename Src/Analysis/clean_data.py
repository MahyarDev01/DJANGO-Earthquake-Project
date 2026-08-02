import os
import re
import sys
import warnings

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(src_dir)
sys.path.append(project_root)

import pandas as pd
from configs import JAPAN_DATASET_CSV, RAW_JAPAN_DATASET_CSV

WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9",
}

MILE_TO_KM = 1.60934


def parse_magnitude(value):

    if pd.isna(value):
        return None
    text = str(value).strip().strip('"').lower()
    if text == "":
        return None

    # already a plain number ("5.1", "4.8")
    try:
        return float(text)
    except ValueError:
        pass


    text = text.replace(" point ", ".")
    text = text.replace(".", " . ")
    rebuilt = ""
    for token in text.split():
        rebuilt += "." if token == "." else WORD_TO_DIGIT.get(token, token)
    try:
        return float(rebuilt)
    except ValueError:
        return None


def parse_depth(value):
    """Convert depth strings with mixed units into a float in kilometers."""
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text == "":
        return None

    match = re.match(r"(-?\d+\.?\d*)\s*(km|kilometers?|miles?|m|meters?)?", text)
    if not match:
        return None

    number = float(match.group(1))
    unit = match.group(2)

    if unit in ("mile", "miles"):
        number = number * MILE_TO_KM
    elif unit in ("m", "meter", "meters"):
        number = number / 1000.0

    return round(number, 2)


def parse_coordinate(value):
    """Convert latitude/longitude, turning 'N/A'/'UNKNOWN'/'' into NaN."""
    if pd.isna(value):
        return None
    text = str(value).strip()
    if text.upper() in ("N/A", "UNKNOWN", ""):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_time(value):

    if pd.isna(value):
        return pd.NaT
    text = str(value).strip().strip('"')
    if text == "":
        return pd.NaT

    is_slash_date = bool(re.match(r"^\d{1,2}/\d{1,2}/\d{4}", text))

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=is_slash_date)
        if pd.isna(parsed) and not is_slash_date:
            # fallback: try day-first parsing for any other ambiguous format
            parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)

    return parsed


def clean_place(value):
    if pd.isna(value):
        return None
    return re.sub(r"\s+", " ", str(value)).strip()


def clean_dataset(input_path=RAW_JAPAN_DATASET_CSV):

    df = pd.read_csv(input_path, dtype=str)

    df["magnitude"] = df["mag"].apply(parse_magnitude)
    df["depth"] = df["depth"].apply(parse_depth)
    df["latitude"] = df["latitude"].apply(parse_coordinate)
    df["longitude"] = df["longitude"].apply(parse_coordinate)
    df["time"] = df["time"].apply(parse_time)
    df["place"] = df["place"].apply(clean_place)

    df = df[["time", "latitude", "longitude", "depth", "magnitude", "place"]]

    return df


def save_cleaned_dataset(input_path=RAW_JAPAN_DATASET_CSV, output_path=JAPAN_DATASET_CSV):

    df = clean_dataset(input_path)
    df.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved: {output_path} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    save_cleaned_dataset()
