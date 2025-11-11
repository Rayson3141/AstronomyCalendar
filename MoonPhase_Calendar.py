import ephem
from datetime import datetime, timedelta

# --- Configuration ---
START_DATE = datetime(2025, 11, 1)
END_DATE = datetime(2025, 12, 31)

PHASES = {
    "New Moon": ephem.next_new_moon,
    "Waxing Crescent": None,
    "First Quarter": ephem.next_first_quarter_moon,
    "Waxing Gibbous": None,
    "Full Moon": ephem.next_full_moon,
    "Waning Gibbous": None,
    "Last Quarter": ephem.next_last_quarter_moon,
    "Waning Crescent": None
}

# --- Function to calculate illumination fraction ---
def moon_illumination(date):
    moon = ephem.Moon()
    moon.compute(date)
    return moon.phase / 100.0  # convert to fraction (0 = new, 1 = full)

# --- Compute all moon phases ---
phase_dates = {phase: [] for phase in PHASES}

# Compute actual major phase dates using ephem
major_phases = ["New Moon", "First Quarter", "Full Moon", "Last Quarter"]

for phase_name in major_phases:
    func = PHASES[phase_name]
    date = START_DATE
    while date <= END_DATE:
        phase_date = ephem.Date(func(date))
        phase_date_dt = phase_date.datetime()
        if phase_date_dt > END_DATE:
            break
        phase_dates[phase_name].append(phase_date_dt.date())
        date = phase_date_dt + timedelta(days=1)

# --- Estimate intermediate phases between major ones ---
sorted_major = []
for phase_name in major_phases:
    for d in phase_dates[phase_name]:
        sorted_major.append((datetime.combine(d, datetime.min.time()), phase_name))
sorted_major.sort()

for i in range(len(sorted_major) - 1):
    d1, phase1 = sorted_major[i]
    d2, phase2 = sorted_major[i + 1]
    delta = d2 - d1

    # midpoints are datetime objects now
    mid1 = d1 + delta / 3
    mid2 = d1 + 2 * delta / 3

    if phase1 == "New Moon" and phase2 == "First Quarter":
        phase_dates["Waxing Crescent"].append(mid1.date())
    elif phase1 == "First Quarter" and phase2 == "Full Moon":
        phase_dates["Waxing Gibbous"].append(mid1.date())
    elif phase1 == "Full Moon" and phase2 == "Last Quarter":
        phase_dates["Waning Gibbous"].append(mid1.date())
    elif phase1 == "Last Quarter" and phase2 == "New Moon":
        phase_dates["Waning Crescent"].append(mid1.date())

# --- Output grouped by phase ---
print(f"Moon Phases between {START_DATE.date()} and {END_DATE.date()}\n")

for phase_name, dates in phase_dates.items():
    print(f"{phase_name}:")
    if dates:
        for d in sorted(dates):
            illum = moon_illumination(ephem.Date(datetime.combine(d, datetime.min.time())))
            print(f"  - {d}  (illumination ≈ {illum*100:.0f}%)")
    else:
        print("  (No occurrences in range)")
    print()
