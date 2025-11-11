from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, get_body
from astroplan import Observer, FixedTarget
import astropy.units as u
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from datetime import timedelta
from zoneinfo import ZoneInfo

# === CONFIGURATION ===
LOCATION_NAME = "Your Location"
LATITUDE = 3.0          # degrees north
LONGITUDE = 101.6       # degrees east
ELEVATION = 50          # meters
TARGET_NAME = "jupiter"    # object name (planet or star)
MIN_ALTITUDE = 5       # degrees
DATE_RANGE_START = "2025-11-11"
DATE_RANGE_END = "2025-12-10"
TIMEZONE = "Asia/Kuala_Lumpur"  # your timezone
OBS_START_HOUR = 21      # local start time (10 PM)
OBS_END_HOUR = 2         # local end time (1 AM next day)
TIME_STEP_MIN = 10       # minutes between samples

# === SETUP ===
location = EarthLocation(lat=LATITUDE*u.deg, lon=LONGITUDE*u.deg, height=ELEVATION*u.m)
observer = Observer(location=location, name=LOCATION_NAME)

# === TARGET LOADING ===
def get_target(name, time):
    planets = ["mercury", "venus", "earth", "mars", "jupiter", "saturn",
               "uranus", "neptune", "pluto", "moon", "sun"]
    if name.lower() in planets:
        coord = get_body(name, time)
        return FixedTarget(coord, name=name)
    else:
        return FixedTarget.from_name(name)

# === TIME RANGE ===
times = Time(np.arange(Time(DATE_RANGE_START).jd, Time(DATE_RANGE_END).jd + 1, 1), format='jd')
num_dates = len(times)
colors = cm.plasma(np.linspace(0, 1, num_dates))  # purple → yellow gradient
local_tz = ZoneInfo(TIMEZONE)

visible_dates = []
fig, ax = plt.subplots(figsize=(10, 6))

# Determine whether the observing window crosses midnight
crosses_midnight = OBS_END_HOUR <= OBS_START_HOUR

# === MAIN LOOP ===
for idx, t in enumerate(times):
    target = get_target(TARGET_NAME, t)

    # Convert reference date to local datetime
    local_date = t.to_datetime(timezone=local_tz)

    # Define start and end of observation window in local time
    start_local = local_date.replace(hour=OBS_START_HOUR, minute=0, second=0, microsecond=0)
    if not crosses_midnight:
        end_local = local_date.replace(hour=OBS_END_HOUR, minute=0, second=0, microsecond=0)
        if end_local <= start_local:
            # fallback guard (shouldn't happen if OBS_END_HOUR > OBS_START_HOUR)
            end_local = start_local + timedelta(hours=(OBS_END_HOUR - OBS_START_HOUR))
    else:
        # crosses midnight: end is on the next day
        end_local = (start_local + timedelta(hours=(24 - OBS_START_HOUR + OBS_END_HOUR)))

    # Create sample datetimes including the end point
    total_minutes = int((end_local - start_local).total_seconds() / 60)
    n_samples = max(2, total_minutes // TIME_STEP_MIN + 1)
    sample_datetimes = [start_local + timedelta(minutes=i * TIME_STEP_MIN) for i in range(n_samples)]
    # ensure last point is exactly end_local
    if sample_datetimes[-1] < end_local:
        sample_datetimes.append(end_local)

    # Convert to astropy Time for altitude computation (astropy handles timezone -> UTC)
    sample_times = Time(sample_datetimes)

    # Get altitude values
    altazs = observer.altaz(sample_times, target)
    altitudes = altazs.alt.deg

    # Compute local_hours for plotting, adjusting for crossing midnight:
    # raw hours: 0..23 + fractional
    raw_hours = np.array([dt.hour + dt.minute / 60.0 + dt.second / 3600.0 for dt in sample_datetimes])
    if crosses_midnight:
        # For continuity, map hours < OBS_START_HOUR to 24+ (i.e., add 24)
        plot_hours = np.where(raw_hours < OBS_START_HOUR, raw_hours + 24.0, raw_hours)
    else:
        plot_hours = raw_hours

    # Check visibility condition
    if np.any(altitudes > MIN_ALTITUDE):
        visible_dates.append(t.iso.split()[0])
        ax.plot(plot_hours, altitudes, color=colors[idx], lw=2, label=t.iso.split()[0])
        # Optional: shade only the portions above the threshold for clarity
        # above_mask = altitudes > MIN_ALTITUDE
        # if np.any(above_mask):
        #     # fill contiguous above-threshold segments
        #     ax.fill_between(plot_hours, altitudes, MIN_ALTITUDE, where=above_mask,
        #                     interpolate=True, color=colors[idx], alpha=0.18)

# === PLOT DECORATION ===
ax.axhline(MIN_ALTITUDE, color='k', ls='--', lw=1, label=f"{MIN_ALTITUDE}° threshold")
ax.set_xlabel("Local Time (hours)")
ax.set_ylabel("Altitude (°)")
ax.set_title(f"{TARGET_NAME} Altitude vs Local Time\n({DATE_RANGE_START}–{DATE_RANGE_END})")

# x limits and xticks: if crossing midnight show e.g. [22,23,24,25] but label 24->0 etc.
if crosses_midnight:
    xmin = OBS_START_HOUR
    xmax = 24 + OBS_END_HOUR
    ax.set_xlim(xmin, xmax)
    # xtick positions and labels
    tick_hours = np.arange(xmin, xmax + 1)
    # convert tick labels back to 0-23 display (mod 24)
    tick_labels = [(int(h) % 24) for h in tick_hours]
    ax.set_xticks(tick_hours)
    ax.set_xticklabels([f"{lab:02d}:00" for lab in tick_labels])
else:
    ax.set_xlim(OBS_START_HOUR, OBS_END_HOUR)
    tick_hours = np.arange(OBS_START_HOUR, OBS_END_HOUR + 1)
    ax.set_xticks(tick_hours)
    ax.set_xticklabels([f"{int(h)%24:02d}:00" for h in tick_hours])

ax.grid(True, alpha=0.4)

# Add colorbar attached to the axis
sm = plt.cm.ScalarMappable(cmap=cm.plasma, norm=plt.Normalize(vmin=0, vmax=num_dates-1))
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax)
cbar.set_label("Date progression")
# show start/end as annotations on colorbar
cbar.ax.text(0.5, 0.02, DATE_RANGE_START, ha='center', va='bottom', transform=cbar.ax.transAxes, fontsize=8)
cbar.ax.text(0.5, 0.95, DATE_RANGE_END, ha='center', va='top', transform=cbar.ax.transAxes, fontsize=8)

# Add legend if not too many dates
if len(visible_dates) <= 15:
    ax.legend(fontsize=8, loc='upper right')

plt.tight_layout()
plt.show()

# === PRINT RESULTS ===
print(f"\nDates when {TARGET_NAME} is above {MIN_ALTITUDE}° between {OBS_START_HOUR}:00 and {OBS_END_HOUR}:00 local time:")
for d in visible_dates:
    print("  ", d)
