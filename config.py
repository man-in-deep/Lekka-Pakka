import os
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL connection (Neon DB)
DATABASE_URL = os.getenv("DATABASE_URL")

# Gemini API key (from Google AI Studio free tier)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# 32 worker types (same as your original list)
WORKER_TYPES = [
    "Labourer", "Harvester", "Helper", "Mazdoor", "Beldar",
    "Loader", "Palledar", "Sweeper", "Waterman", "Herder",
    "Dishwasher", "Apprentice", "Assistant", "Guard", "Attendant",
    "Operator", "Moulder", "Driver", "Watchman", "Laundryman",
    "Stitcher", "Khalasi", "Mechanic", "Mason", "Carpenter",
    "Electrician", "Welder", "Plumber", "Painter", "Driller",
    "Tailor"
]

# Regions with priority – only the first one is queried from Gemini.
# Rates for Ibrahimpatnam and Araku Valley are derived.
REGIONS = [
    {"priority": 1, "name": "Gajuwaka, Visakhapatnam"},
    {"priority": 2, "name": "Ibrahimpatnam, Vijayawada"},
    {"priority": 3, "name": "Araku Valley"}
]