import swisseph as swe
import timezonefinder
import pytz
from datetime import datetime

# Zodiac signs
ZODIAC_SIGNS = [
    ("Aries", 0, 30), ("Taurus", 30, 60), ("Gemini", 60, 90), ("Cancer", 90, 120),
    ("Leo", 120, 150), ("Virgo", 150, 180), ("Libra", 180, 210), ("Scorpio", 210, 240),
    ("Sagittarius", 240, 270), ("Capricorn", 270, 300), ("Aquarius", 300, 330), ("Pisces", 330, 360)
]

# Major planets
PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mercury": swe.MERCURY, "Venus": swe.VENUS,
    "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN,
    "Uranus": swe.URANUS, "Neptune": swe.NEPTUNE, "Pluto": swe.PLUTO,
    "North Node": swe.MEAN_NODE
}

# Major aspects with orbs
ASPECTS = {
    "Conjunction": (0, 8), "Opposition": (180, 8),
    "Trine": (120, 6), "Square": (90, 6), "Sextile": (60, 4)
}

def get_zodiac_sign(degree):
    """Returns the zodiac sign and position within the sign."""
    for sign, start, end in ZODIAC_SIGNS:
        if start <= degree < end:
            sign_degree = degree - start
            deg = int(sign_degree)
            minutes = int((sign_degree - deg) * 60)
            return sign, f"{sign} {deg}°{minutes}′"
    return "Unknown", "Unknown"

def get_planet_positions(jd_ut, lat, lon):
    """Calculates planetary positions."""
    house_cusps = get_house_cusps (jd_ut, lat, lon)
    positions = {}
    for planet, planet_id in PLANETS.items():
        pos, _ = swe.calc_ut(jd_ut, planet_id)
        sign, formatted_pos = get_zodiac_sign(pos[0])
        house = get_house_for_planet(pos[0], house_cusps)
        positions[planet] = {"sign": sign, "degree": pos[0], "house": house, "formatted": formatted_pos + f", House: {house}"}
    return positions

def get_house_cusps(jd_ut, lat, lon, house_system=b"P"):
    """Calculates house cusps based on Placidus system.
        House Systems:
    - "P" = Placidus (default)
    - "W" = Whole Sign
    - "K" = Koch
    - "R" = Regiomontanus
    - "E" = Equal Houses
    - "C" = Campanus
    """
    houses = swe.houses(jd_ut, lat, lon, house_system)
    house_positions = {}
    for i in range(12):
        sign, formatted_pos = get_zodiac_sign(houses[0][i])
        house_positions[f"House {i+1}"] = {"degree": houses[0][i], "sign": sign, "formatted": formatted_pos}
    return house_positions


def get_house_for_planet(planet_degree, house_cusps):
    """Determines which house a planet is in, handling zodiac wrap-around cases correctly."""
    house_numbers = list(range(1, 13))
    house_degrees = [house_cusps[f"House {i}"]["degree"] for i in house_numbers]

    for i in range(12):
        next_i = (i + 1) % 12  # Wrap around at 12th house
        house_start = house_degrees[i]
        house_end = house_degrees[next_i]

        # Normal case: house_start < planet_degree < house_end
        if house_start <= planet_degree < house_end:
            return i + 1

        # Wrap-around case: e.g., 29° Pisces to 0° Aries
        if house_end < house_start:
            if planet_degree >= house_start or planet_degree < house_end:
                return i + 1

    return "UNKNOWN"  # Default case if nothing matches


def get_aspects(planet_positions, house_cusps):
    """Determines aspects between planets"""
    aspect_list = []
    planets = list(planet_positions.keys())

    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            planet1, pos1 = planets[i], planet_positions[planets[i]]["degree"]
            planet2, pos2 = planets[j], planet_positions[planets[j]]["degree"]

            # Handle cases where aspect crosses 0° Aries
            angle = abs(pos1 - pos2)
            if angle > 180:
                angle = 360 - angle

            for aspect, (exact, orb) in ASPECTS.items():
                if abs(angle - exact) <= orb:
                    house1 = get_house_for_planet(pos1, house_cusps)
                    house2 = get_house_for_planet(pos2, house_cusps)

                    aspect_list.append(
                        f"{planet1} in House {house1} and {planet_positions[planet1]['sign']} "
                        f"{aspect} {planet2} in House {house2} and {planet_positions[planet2]['sign']} "
                        f"({angle:.2f}°)"
                    )

    return aspect_list


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


def get_full_chart(birth_datetime, lat, lon):
    """Computes planetary positions, house cusps, and aspects."""
    jd_ut = get_julian_day(birth_datetime, lat, lon)

    # Compute planetary positions
    planet_positions = get_planet_positions(jd_ut, lat, lon)

    # Compute house cusps
    house_cusps = get_house_cusps(jd_ut, lat, lon)

    # Compute aspects with house/sign data
    aspects = get_aspects(planet_positions, house_cusps)

    return {
        "Planetary Positions": {p: data["formatted"] for p, data in planet_positions.items()},
        "House Cusps": {h: data["formatted"] for h, data in house_cusps.items()},
        "Aspects": aspects
    }


if __name__ == "__main__":
    swe.set_ephe_path('/path/to/ephe')

    # Example: August 8, 1986, 19:40 Moscow, Russia
    birth_date = "1986-08-13"
    birth_time = "19:40"
    latitude = 55.7558
    longitude = 37.6173

    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")

    chart = get_full_chart(birth_datetime, latitude, longitude)

    print("\n🔹 Planetary Positions:")
    for planet, position in chart["Planetary Positions"].items():
        print(f"{planet}: {position}")

    print("\n🔹 House Cusps:")
    for house, position in chart["House Cusps"].items():
        print(f"{house}: {position}")

    print("\n🔹 Aspects:")
    for aspect in chart["Aspects"]:
        print(aspect)


