import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini 2.0 Flash-Lite (or whatever free model you have in AI Studio)
model = genai.GenerativeModel('gemini-3.1-flash-lite')

def get_hourly_rate(worker_type, location):
    """
    Query Gemini for the average hourly wage of `worker_type` in `location`.
    Returns a float (INR).
    """
    prompt = (
        f"What is the average hourly wage rate for a {worker_type} "
        f"in {location}? Give only the numeric amount in Indian Rupees. "
        "No additional text."
    )
    try:
        response = model.generate_content(prompt)
        # Clean the response: remove commas, convert to float
        rate = float(response.text.strip().replace(',', ''))
        return rate
    except Exception as e:
        # If anything fails, return a safe default
        print(f"Gemini error for {worker_type} in {location}: {e}")
        return 50.0