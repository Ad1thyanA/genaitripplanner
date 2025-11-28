import pandas as pd

SOURCE = "data/Top Indian Places to Visit.csv"
TARGET = "data/tourism_data.csv"

df = pd.read_csv(SOURCE)

print("Detected columns:", df.columns)

out = pd.DataFrame()

# Basic fields
out["name"] = df["Name"].astype(str)
out["city"] = df["City"].fillna("").astype(str)
out["state"] = df["State"].fillna("").astype(str)

# Region from Zone
out["region"] = df["Zone"].fillna("India").astype(str)

# Tags from Type
out["tags"] = df["Type"].fillna("tourist attraction").astype(str)

# Description from Significance
out["description"] = df["Significance"].fillna("Popular tourist attraction").astype(str)

# Duration hours
if "time needed to visit in hrs" in df.columns:
    out["typical_duration_hours"] = (
        df["time needed to visit in hrs"].fillna(2).astype(int)
    )
else:
    out["typical_duration_hours"] = 3

# Cost level from Entrance fee
def cost_level_from_fee(fee):
    try:
        fee = float(fee)
    except:
        return "medium"
    if fee == 0:
        return "low"
    if fee <= 200:
        return "medium"
    return "high"

out["cost_level"] = df["Entrance Fee in INR"].apply(cost_level_from_fee)

# Best season from dataset
if "Best Time to visit" in df.columns:
    out["best_season"] = df["Best Time to visit"].fillna("Oct-Mar")
else:
    out["best_season"] = "Oct-Mar"

# Extra metadata: rating & review count
out["rating"] = df["Google review rating"].fillna(0).astype(float)
out["review_count_lakhs"] = df["Number of google review in lakhs"].fillna(0).astype(float)

out.to_csv(TARGET, index=False)

print(f"Saved ✨ cleaned tourism_data.csv with {len(out)} rows")
