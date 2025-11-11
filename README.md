# Astronomy Visibility Calendar Generator

This Python project generates a visibility calendar for astronomical objects from any location and timezone using Astroplan and Astropy. It helps observers determine when objects are visible and reach their highest altitude. The script supports Solar System bodies, fixed deep-sky objects, and custom RA/Dec coordinates, and can optionally plot altitude vs time for a sample night. All configuration values are placeholders for easy customization: location, target, date range, minimum altitude, and timezone.

Features:
- Compute rise, set, and transit times for celestial objects
- Determine maximum altitude to find optimal observing nights
- Track planets, Moon, Sun, stars, clusters, nebulae, galaxies, or manual coordinates
- Optional altitude plots for a sample night
- Advanced tracking (satellites via skyfield/sgp4, comets/asteroids via astroquery.jplhorizons, transients/GRBs via VOEvents or NASA APIs)

Supported Targets:
- Solar System objects (via astropy.coordinates.get_body): sun, moon, mercury, venus, mars, jupiter, saturn, uranus, neptune, pluto
- Fixed deep-sky objects (via FixedTarget.from_name): stars like Vega, Sirius, Betelgeuse; open clusters like Pleiades, Hyades; globular clusters like M13, Omega Centauri; galaxies like Andromeda Galaxy, M31; nebulae like Orion Nebula, Lagoon Nebula
- Custom coordinates (via SkyCoord + FixedTarget) for any RA/Dec

Usage:
- Configure placeholders in the script: LOCATION_NAME, LATITUDE, LONGITUDE, ELEVATION, TARGET_NAME, MIN_ALTITUDE, DATE_RANGE_START, DATE_RANGE_END, TIMEZONE
- Run the script to see dates when the target is above the minimum altitude with transit altitude
- Optionally view altitude vs time plots for a chosen night

Example Output:
Days when Mars is higher than 40°:
2025-11-01: transit altitude 55.3°
2025-11-03: transit altitude 57.1°
2025-11-05: transit altitude 59.0°
...

License:
Open-source and free for personal and educational use

Acknowledgments:
Astroplan, Astropy, Matplotlib
