import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict

# Reading the file
crime = pd.read_csv("2020_crime_loc_coords.csv")

# We're only looking for Berkeley
city_state_country = ",Berkeley,California,United States"

# Geocoding function.
def geocode(address):
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey=3155bb614fcd4b808d7ed2b2beca8541"
    resp = requests.get(url)
    data = resp.json()

    if data["features"][0]["properties"]["county"] != "Alameda County":
        return None, None

    return data["features"][0]["properties"]["lon"], data["features"][0]["properties"]["lat"]

# Geocoding for every line. Each time update.
# (IMPORTANT!!!) When restarting, change D
D = 1510
for i in range(2200):

    # If address is empty, pass
    if pd.isna(crime.loc[i+D, "Location"]):
        continue

    lon, lat = geocode(crime.loc[i+D, "Location"]+city_state_country)
    crime.loc[i+D, "lon"] = lon
    crime.loc[i+D, "lat"] = lat
    print(f"[{i+D}] {crime.loc[i+D, "Location"]+city_state_country} → lon={lon}, lat={lat}")
    crime.to_csv("2020_crime_loc_coords.csv", index=False)