import numpy as np
import pandas as pd
import re

address = pd.read_csv("Berkeley Address Coordinates.csv")
crime = pd.read_csv("SAMPLE_crime_data_parsed_no_page_deduped.csv")

# Excluding uesless data for convenience
address_sorted = address[["number", "street", "lon", "lat"]]
crime_sorted = crime[["Location"]]

# Lower case conversion for convenience
address_sorted["street"] = address_sorted["street"].astype(str).str.lower()
crime_sorted["Location"] = crime_sorted["Location"].astype(str).str.lower()

# Splitting numbers and streets for crime_sorted
crime_sorted["number"] = np.nan
crime_sorted["street"] = np.nan

# Last words are typically rd, st , etc. We want to get rid of it for convenience.
def remove_last_word(text):
    # Just in case there are spaces
    text = text.strip()
    
    # If empty, skip
    if text == "":
        return text

    # ex)"channing way" -> ["channing", "way"]
    words = text.split()

    # If 2 or more words, delete the last word
    if len(words) > 1:
        return " ".join(words[:-1])
    # If there are only one word, keep the original
    else:
        return text
address_sorted["street"] = address_sorted["street"].apply(remove_last_word)

# Splitting numbers and street names for location in crime_sorted
for i, loc in enumerate(crime_sorted["Location"]):

    # Making sure that there are no spaces front and back. If empty or no string, pass.
    if not isinstance(loc, str) or loc.strip() == "":
        continue
    s = loc.strip()

    # Detach numbers, rest goes into street
    match = re.match(r"^(\d+)\s*(.*)", s)
    if match:
        number = match.group(1)
        street = match.group(2).strip()
        crime_sorted.at[i, "number"] = number
        crime_sorted.at[i, "street"] = street
    
    # If no numbers, number: nan, street: building
    else:
        crime_sorted.at[i, "number"] = np.nan
        crime_sorted.at[i, "street"] = s

# Now we want to see if the street names for crime_sorted actually in the address.csv.
# First, set up a list of street names from address_sorted.
valid_streets = set(address_sorted["street"].dropna().unique())

# Simplify the street names
def keep_only_valid_street(street):

    # As before, If empty or no string, pass.
    if not isinstance(street, str) or street.strip() == "":
        return street

    # Inspect each word
    words = street.split()

    # If the name of the street is actually in the crime_sorted street, leave only the street name
    for w in words:
        if w in valid_streets:
            return w  

    # If not, just leave it
    return street
crime_sorted["street"] = crime_sorted["street"].apply(keep_only_valid_street)

# Using only valid address with both numbers and street names
address_valid = address_sorted[address_sorted["number"].notna() & address_sorted["street"].notna()]
address_dict = {}
for _, row in address_valid.iterrows():
    try:
        num = int(row["number"])
        st = str(row["street"]).strip()
        address_dict[(num, st)] = (row["lon"], row["lat"])
    except:
        continue

# iterating each row, see if anything matches
for i, row in crime_sorted.iterrows():
    num = row["number"]
    st = row["street"]

    # We don't count Nan
    if pd.isna(num) or pd.isna(st):
        continue

    try:
        num = int(num)
        st = str(st).strip()
    except:
        continue

    key = (num, st)

    # If matches, insert lon and lat
    if key in address_dict:
        crime_sorted.at[i, "lon"] = address_dict[key][0]
        crime_sorted.at[i, "lat"] = address_dict[key][1]

# Adding the coordinate info to the original file
coords = crime_sorted[["lon", "lat"]]
crime_with_coords = pd.concat([crime, coords], axis=1)
crime_with_coords.to_csv("SAMPLE_crime_data_with_coords.csv", index=False)