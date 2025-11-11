import ephem
from datetime import datetime, timedelta

# --- Configuration ---
START_DATE = datetime(2025, 11, 1)
END_DATE = datetime(2025, 12, 31)
MIN_ILLUMINATION = 20  # minimum percentage
MAX_ILLUMINATION = 50  # maximum percentage

# --- Generate dates ---
date = START_DATE
good_dates = []

while date <= END_DATE:
    moon = ephem.Moon(date)
    illumination = moon.phase  # 0=new, 100=full
    if MIN_ILLUMINATION <= illumination <= MAX_ILLUMINATION:
        good_dates.append((date.date(), illumination))
    date += timedelta(days=1)

# --- Print results ---
print(f"Dates with Moon illumination between {MIN_ILLUMINATION}% and {MAX_ILLUMINATION}%:")
for d, illum in good_dates:
    print(f"{d}: {illum:.1f}% illumination")
