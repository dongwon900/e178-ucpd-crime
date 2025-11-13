import pandas as pd
import re

# Reading the file
crime = pd.read_csv("SAMPLE_crime_data_parsed_no_page_deduped.csv")

# Adding [lon] and [lat]
crime["lon"] = None
crime["lat"] = None

# Deleting everything else except number, alphabet, and " "
crime["Location"] = crime["Location"].str.replace(r"[^A-Za-z0-9\s]", "", regex=True)

# We want to ignore all the extra info after st, rd, blvd, etc.
last_words = [
    "st", "street", "rd", "road", "ave", "av", "avenue", "blvd", "boulevard", "way", "wy", "ct", "court", "lot", 
    "dr", "drive", "ln", "lane", "pl", "place", "cir", "circle", "ter", "terrace", "walk", "path", "hall"
]
pattern = r"\b(" + "|".join(last_words) + r")\b.*"
crime["Location"] = crime["Location"].str.replace(pattern, r"\1", regex=True, flags=re.IGNORECASE)

#Update
crime.to_csv("crime_loc_coords_buffer.csv", index=False)