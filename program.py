import ephem
from datetime import datetime
import swisseph as swe
import timezonefinder
import pytz

# Set the path to your ephemeris files (update the path below)
swe.set_ephe_path('/path/to/ephe')

# Define zodiac signs and their degree ranges
ZODIAC_SIGNS = [
    ("Aries", 0, 30),
    ("Taurus", 30, 60),
    ("Gemini", 60, 90),
    ("Cancer", 90, 120),
    ("Leo", 120, 150),
    ("Virgo", 150, 180),
    ("Libra", 180, 210),
    ("Scorpio", 210, 240),
    ("Sagittarius", 240, 270),
    ("Capricorn", 270, 300),
    ("Aquarius", 300, 330),
    ("Pisces", 330, 360)
]

# List of major planets in Swiss Ephemeris
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.MEAN_NODE  # Mean North Node (Rahu)
}

def get_zodiac_sign(degree):
    """Returns the zodiac sign and position within the sign."""
    for sign, start, end in ZODIAC_SIGNS:
        if start <= degree < end:
            sign_degree = degree - start
            deg = int(sign_degree)
            minutes = int((sign_degree - deg) * 60)
            return f"{sign} {deg}°{minutes}′"
    return "Unknown"


def get_timezone_offset(birth_datetime, lat, lon):
    """Returns the timezone offset (UTC) for the given date and location."""
    tf = timezonefinder.TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)

    if not timezone_str:
        raise ValueError("Could not determine the timezone for the given location.")

    # Get timezone object
    tz = pytz.timezone(timezone_str)

    # Convert birth date to a timezone-aware datetime object
    dt = datetime(birth_datetime.year, birth_datetime.month, birth_datetime.day, birth_datetime.hour, 0)
    localized_dt = tz.localize(dt, is_dst=None)

    # Return UTC offset in hours
    return localized_dt.utcoffset().total_seconds() / 3600


def get_julian_day(birth_datetime, lat, lon):
    
    tz_offset = get_timezone_offset(birth_datetime, lat, lon)

    # Convert local time to UT:
    hour_ut = birth_datetime.hour - tz_offset + (birth_datetime.minute / 60.0)
    return swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, hour_ut)


def get_planet_positions(birth_date, birth_time, lat, lon):
    """
    Calculates planetary positions for a given birth date and time.
    
    Parameters:
    - year, month, day, hour: Date & time of birth (24-hour format)
    - tz_offset: Timezone offset (e.g., +4 for Moscow)
    
    Returns:
    - dict: Planetary placements with zodiac sign and degrees
    """
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")

    # Convert birth date to Julian Day (convert local time to UT)
    jd_ut = get_julian_day(birth_datetime, lat, lon)

    # Get planetary positions
    placements = {}
    for planet, planet_id in PLANETS.items():
        pos, _ = swe.calc_ut(jd_ut, planet_id)
        placements[planet] = get_zodiac_sign(pos[0])

    # Print planetary placements
    for planet, position in placements.items():
        print(f"{planet}: {position}")



def get_natal_houses(birth_date, birth_time, lat, lon):
    # --- Calculate House Cusps ---
   
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    # Convert birth date to Julian Day (convert local time to UT)
    jd_ut = get_julian_day(birth_datetime, lat, lon)

    # Use the Placidus house system (default). You can change the system if needed.
    house_cusps, ascmc = swe.houses(jd_ut, lat, lon)
    
    print("\nHouse Cusps:")
    placements = {}
    for i, cusp in enumerate(house_cusps, start=0):
        placements[i] = get_zodiac_sign(house_cusps[i])


    # Print house placements
    for i, position in placements.items():
        print(f"House {i+1}: {position}")


    # Ascendant (the 1st house cusp) is typically ascmc[0]
    #ascendant = ascmc[0]
    #print(f"\nAscendant (Rising): {ascendant:.2f}°")



def get_house_cusps(jd_ut, lat, lon, house_system="P"):
    """
    Calculates house cusps for a given Julian Day and location.
    
    House Systems:
    - "P" = Placidus (default)
    - "W" = Whole Sign
    - "K" = Koch
    - "R" = Regiomontanus
    - "E" = Equal Houses
    - "C" = Campanus
    
    Returns:
    - Dictionary of house cusps
    """
    cusps, ascmc = swe.houses(jd_ut, lat, lon, house_system)
    
    house_data = {f"House {i+1}": round(cusps[i], 2) for i in range(12)}
    house_data["Ascendant"] = round(ascmc[0], 2)  # Ascendant (1st house cusp)
    house_data["MC (Midheaven)"] = round(ascmc[1], 2)  # Midheaven (10th house cusp)
    
    return house_data


def assign_planets_to_houses(planet_positions, house_cusps):
    """
    Assigns planets to houses based on their degree positions.
    
    Returns:
    - Dictionary mapping each planet to a house.
    """
    planet_houses = {}

    house_degrees = list(house_cusps.values())[:12]  # First 12 entries are house cusps
    house_degrees.append(house_degrees[0] + 360)  # Wrap around for 12th house boundary

    for planet, pos in planet_positions.items():
        planet_degree = float(pos.split(" ")[1].split("°")[0])  # Extract numeric degree
        sign = pos.split(" ")[0]  # Extract sign name

        # Convert sign + degree to absolute ecliptic longitude
        sign_offset = {s: start for s, start, _ in ZODIAC_SIGNS}[sign]
        absolute_degree = sign_offset + planet_degree

        # Determine which house the planet falls into
        for i in range(12):
            if house_degrees[i] <= absolute_degree < house_degrees[i + 1]:
                planet_houses[planet] = f"House {i+1}"
                break

    return planet_houses


def calculate_aspect(angle1, angle2, orb=6):
    # Calculate the absolute difference
    diff = abs(angle1 - angle2) % 360
    if diff > 180:
        diff = 360 - diff
    # Check for a specific aspect (e.g., conjunction if diff < orb)
    if diff < orb:
        return True
    return False



# Test it

# Moscow coordinates (approximate):
# latitude = 55.7558    # North
# longitude = 37.6176   # East

#get_planet_positions("1986-08-13", "19:40", 55.7558, 37.6176)
get_natal_houses("1986-08-13", "19:40", 55.7558, 37.6176)

#chart2 = get_natal_houses()
#print(chart2)
