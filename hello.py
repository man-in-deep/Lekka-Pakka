import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# ✅ Use the free model you have (Flash-Lite or Flash)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

WORKER_TYPES = [
    "Labourer", "Harvester", "Helper", "Mazdoor", "Beldar",
    "Loader", "Palledar", "Sweeper", "Waterman", "Herder",
    "Dishwasher", "Apprentice", "Assistant", "Guard", "Attendant",
    "Operator", "Moulder", "Driver", "Watchman", "Laundryman",
    "Stitcher", "Khalasi", "Mechanic", "Mason", "Carpenter",
    "Electrician", "Welder", "Plumber", "Painter", "Driller",
    "Tailor"
]

def get_rate_for_visakhapatnam(worker):
    prompt = (
        f"What is the average hourly wage rate for a {worker} "
        f"in Gajuwaka, Visakhapatnam? Give only the numeric amount "
        "in Indian Rupees. No additional text."
    )
    try:
        response = model.generate_content(prompt)
        rate = float(response.text.strip().replace(',', ''))
        return rate
    except Exception as e:
        print(f"  Error for {worker}: {e}")
        return 50.0   # fallback

def main():
    total = len(WORKER_TYPES)
    results = []
    print(f"Calling Gemini for {total} workers (Visakhapatnam only)…")
    count = 0

    for worker in WORKER_TYPES:
        base_rate = get_rate_for_visakhapatnam(worker)
        # Derive the three rates with minimum ₹10
        rate1 = base_rate
        rate2 = max(10, base_rate - 10)
        rate3 = max(10, base_rate - 20)

        # Priority 1 (Gajuwaka, Visakhapatnam)
        results.append(f"1-{worker}-{rate1}")
        # Priority 2 (Ibrahimpatnam, Vijayawada)
        results.append(f"2-{worker}-{rate2}")
        # Priority 3 (Araku Valley)
        results.append(f"3-{worker}-{rate3}")

        count += 1
        print(f"[{count}/{total}] {worker} → Base: ₹{rate1} | P2: ₹{rate2} | P3: ₹{rate3}")

        # Respect free tier (15 RPM)
        time.sleep(4)

    print(f"\n✅ Done! Generated {len(results)} total rows (should be 96).")
    if len(results) == 96:
        print("All 96 entries successfully created.")
    else:
        print(f"⚠️ Expected 96, got {len(results)}")

    # Save to file for inspection
    with open("wages_output.txt", "w") as f:
        f.write("\n".join(results))
    print("Saved to wages_output.txt")

if __name__ == "__main__":
    main()