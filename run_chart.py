from datetime import datetime
import swisseph as swe
from astro_chart import generate_chatgpt_prompt, get_full_chart  # Import your function

# Set path to Swiss Ephemeris files
swe.set_ephe_path('/path/to/ephe')  # Update with actual path

# Input birth details
birth_date = "1986-08-13"
birth_time = "19:40"
latitude = 55.7558
longitude = 37.6173

# Convert to datetime object
birth_datetime = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")

# Generate chart
chart = get_full_chart(birth_datetime, latitude, longitude)

print("\n🔹 House Cusps:")
for house, position in chart["House Cusps"].items():
    print(f"{house}: {position}")

# Print output
print("\n🔹 Planetary Positions:")
for planet, position in chart["Planetary Positions"].items():
    print(f"{planet}: {position}")

print("\n🔹 Aspects:")
for aspect in chart["Aspects"]:
    print(aspect)

print("\n🔹 Chat GPT Prompt:")
prompt = generate_chatgpt_prompt(chart)

print(prompt)  # Copy-paste into ChatGPT for analysis