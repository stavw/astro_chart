import pdb
import pytest
from datetime import datetime
from astro_chart import get_zodiac_sign, get_house_for_planet, get_aspects, get_julian_day, get_full_chart

# Sample house cusps for testing
SAMPLE_HOUSE_CUSPS = {
    "House 1": {"degree": 5},
    "House 2": {"degree": 30},
    "House 3": {"degree": 60},
    "House 4": {"degree": 90},
    "House 5": {"degree": 120},
    "House 6": {"degree": 150},
    "House 7": {"degree": 180},
    "House 8": {"degree": 210},
    "House 9": {"degree": 240},
    "House 10": {"degree": 270},
    "House 11": {"degree": 300},
    "House 12": {"degree": 330},
}

def test_get_zodiac_sign():
    assert get_zodiac_sign(10) == ("Aries", "Aries 10°0′")
    assert get_zodiac_sign(120) == ("Leo", "Leo 0°0′")
    assert get_zodiac_sign(359) == ("Pisces", "Pisces 29°0′")


def test_get_house_for_planet():
    """Test planet placement for all 12 houses."""
    house_cusps = {
        "House 1": {"degree": 10},
        "House 2": {"degree": 40},
        "House 3": {"degree": 70},
        "House 4": {"degree": 100},
        "House 5": {"degree": 130},
        "House 6": {"degree": 160},
        "House 7": {"degree": 190},
        "House 8": {"degree": 220},
        "House 9": {"degree": 250},
        "House 10": {"degree": 280},
        "House 11": {"degree": 310},
        "House 12": {"degree": 340},
    }

    # Define test cases covering each house boundary
    test_cases = [
        (15, 1),   # House 1 (10° - 40°)
        (45, 2),   # House 2 (40° - 70°)
        (75, 3),   # House 3 (70° - 100°)
        (105, 4),  # House 4 (100° - 130°)
        (135, 5),  # House 5 (130° - 160°)
        (165, 6),  # House 6 (160° - 190°)
        (195, 7),  # House 7 (190° - 220°)
        (225, 8),  # House 8 (220° - 250°)
        (255, 9),  # House 9 (250° - 280°)
        (285, 10), # House 10 (280° - 310°)
        (315, 11), # House 11 (310° - 340°)
        (345, 12), # House 12 (340° - 10° wrap-around)
        (5, 12),   # House 12 wrap-around (340° - 10°)
    ]

    for planet_degree, expected_house in test_cases:
        result = get_house_for_planet(planet_degree, house_cusps)
        assert result == expected_house, f"Planet at {planet_degree}° should be in House {expected_house}, but got {result}"


def test_get_aspects():
    positions = {
        "Sun": {"sign": "Aries","degree": 0, "house": 1},
        "Moon": {"sign": "Libra","degree": 180, "house": 6},
        "Mars": {"sign": "Twins","degree": 120, "house": 4},
        "Venus": {"sign": "Taurus","degree": 60, "house": 2}
    }
    house_cusps = {
        "House 1": {"degree": 10},
        "House 2": {"degree": 40},
        "House 3": {"degree": 70},
        "House 4": {"degree": 100},
        "House 5": {"degree": 130},
        "House 6": {"degree": 160},
        "House 7": {"degree": 190},
        "House 8": {"degree": 220},
        "House 9": {"degree": 250},
        "House 10": {"degree": 280},
        "House 11": {"degree": 310},
        "House 12": {"degree": 340},
    }
    #pdb.set_trace()
    aspects = get_aspects(positions, house_cusps)
    assert "Sun in House 12 and Aries Opposition Moon in House 6 and Libra" in aspects
    assert "Sun in House 12 and Aries Trine Mars in House 4 and Twins" in aspects
    assert "Sun in House 12 and Aries Sextile Venus in House 2 and Taurus" in aspects
    assert "Moon in House 6 and Libra Sextile Mars in House 4 and Twins" in aspects
    assert "Moon in House 6 and Libra Trine Venus in House 2 and Taurus" in aspects
    assert "Mars in House 4 and Twins Sextile Venus in House 2 and Taurus" in aspects

def test_get_julian_day():
    birth_datetime = datetime(1986, 8, 13, 19, 40)
    jd = get_julian_day(birth_datetime, 55.7558, 37.6173)
    assert jd > 0

def test_full_chart():
    birth_date = "1986-08-13"
    birth_time = "19:40"
    latitude = 55.7558
    longitude = 37.6173
    birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    chart = get_full_chart(birth_datetime, latitude, longitude)
    assert "Sun in House 7 and Leo Trine Uranus in House 11 and Sagittarius" in chart["Aspects"][0]
    assert "Sun in House 7 and Leo Trine North Node in House 2 and Aries" in chart["Aspects"][1]
    assert "Moon in House 10 and Scorpio Trine Mercury in House 7 and Leo" in chart["Aspects"][2]
    assert "Moon in House 10 and Scorpio Conjunction Saturn in House 10 and Sagittarius" in chart["Aspects"][3]
    assert "Mercury in House 7 and Leo Trine Saturn in House 10 and Sagittarius" in chart["Aspects"][4]
    assert "Mercury in House 7 and Leo Square Pluto in House 9 and Scorpio" in chart["Aspects"][5]
    assert "Venus in House 8 and Libra Square Mars in House 12 and Capricorn" in chart["Aspects"][6]
    assert "Venus in House 8 and Libra Sextile Saturn in House 10 and Sagittarius" in chart["Aspects"][7]
    assert "Venus in House 8 and Libra Square Neptune in House 12 and Capricorn" in chart["Aspects"][8]
    assert "Jupiter in House 2 and Pisces Square Uranus in House 11 and Sagittarius" in chart["Aspects"][9]
    assert "Uranus in House 11 and Sagittarius Trine North Node in House 2 and Aries" in chart["Aspects"][10]
    assert "Neptune in House 12 and Capricorn Sextile Pluto in House 9 and Scorpio" in chart["Aspects"][11]