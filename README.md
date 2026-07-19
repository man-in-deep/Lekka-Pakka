# Labour Management System (Lekka-Pakka)

A location‑based, AI‑powered platform for daily‑wage workers and contractors in Andhra Pradesh.

## Demo Video

Watch the full working of the project:  
https://drive.google.com/file/d/YOUR_VIDEO_ID/view

(Replace YOUR_VIDEO_ID with the actual ID from your Google Drive link.)

---

## Why this project?

In Andhra Pradesh, daily‑wage workers like masons, carpenters, and sweepers often do not know the fair hourly rate for their trade in a given area. Contractors may pay them less, and there is no simple record of what they earned each day.

This system solves that by:

- Automatically calculating the correct hourly wage based on the worker's exact location
- Giving every labourer and contractor a simple, password‑free identity
- Tracking daily earnings so workers can compare what they earned vs what they were actually paid

---

## How it works (overview)

### 1. Login without password
- The user clicks "Proceed" on the login page.
- The browser creates a unique device ID (like a long random number) and stores it.
- This ID becomes the user's identity – no username, no password, no registration.
- The same device always gets the same ID, even after restarting.

### 2. Wage data from AI
- The system uses Google Gemini (free tier) to ask for the hourly wage of 32 worker types in Visakhapatnam (Gajuwaka).
- For Ibrahimpatnam, the rate is 10 rupees less. For Araku Valley, it's 20 rupees less.
- All 96 rates (32 workers × 3 areas) are stored in a database and refreshed every 15 days automatically.

### 3. Map and location detection
- The map shows circles (green, yellow, red) loaded from an Excel file.
- Each circle represents a mandal with a priority: 1 (green) = high cost, 2 (yellow) = medium, 3 (red) = low.
- When the user opens their dashboard, the browser finds their GPS location and checks which circles they are inside.

### 4. Wage calculation algorithm
The final hourly rate is computed based on the intersecting circles.

**If only one priority is present (e.g., only green):**
- Base rate for that priority is taken from the database.
- A bonus is added: 20% for green, 15% for yellow, 10% for red.
- Formula: `final = base_rate * (1 + bonus_percent/100)`

**If multiple priorities are present (e.g., green + yellow):**
- For each intersecting circle, the base rate for its priority is taken.
- The average of these base rates is calculated.
- Then, for each circle, an extra percentage is added based on its priority:
  - Green: extra 10% of its base rate
  - Yellow: extra 7.5% of its base rate
  - Red: extra 5% of its base rate
- Subtotal = average + sum of all extras
- Formula: `final = subtotal * 1.05` (the 5% accounts for inflation)

The result is the correct hourly wage for that worker in that exact location.

### 5. Daily earnings tracking
- The labourer selects their profession from a dropdown, enters hours worked (max 10), and sees a preview of the day's earnings.
- They can enter how much the contractor actually paid.
- Both calculated and actual amounts are saved to the database.
- A history table shows all past entries, and a bar chart compares calculated vs received pay over the last 7 days.

### 6. Multilingual support
- The interface supports English, Telugu, and Hindi.
- All text, including worker type names in the dropdown, changes when a language button is clicked.

---

## Why this is important for Andhra Pradesh

- Wages vary widely between urban (Visakhapatnam) and rural (Araku Valley) areas.
- Many labourers are not literate in English or comfortable with complex apps.
- Contractors need quick, accurate cost estimates for different locations.
- This system removes information gaps and creates a transparent, fair record for both sides.

---

## Technology used

- **Backend:** Python (Flask)
- **Database:** PostgreSQL (Neon serverless)
- **AI:** Google Gemini 2.0 Flash‑Lite (free tier)
- **Maps:** Leaflet.js + OpenStreetMap (no API key needed)
- **Charts:** Chart.js
- **Scheduling:** APScheduler
- **Excel reading:** openpyxl
- **Deployment:** Render (free tier)

---

## How to run locally

1. Install dependencies: `pip install -r requirements.txt`
2. Create a `.env` file with:
   - `DATABASE_URL=your_postgres_url`
   - `GEMINI_API_KEY=your_gemini_api_key`
3. Place your `AP_District_Mandal_Priority.xlsx` in the root folder.
4. Run `python app.py`
5. Open `http://127.0.0.1:5000`

---

## Deployment on Render

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Add the same environment variables in the Render dashboard.
- To keep the free service awake, set up a free cron job (e.g., cron-job.org) to ping the site every 14 minutes.

---

## Project structure (key files)

- `app.py` – Routes for admin, contractor, labour
- `database.py` – All database functions and 15‑day refresh logic
- `gemini_service.py` – Fetches base wages from Gemini
- `excel_reader.py` – Reads the Excel file with circle data
- `templates/` – HTML pages with government‑theme design
- `static/` – CSS, JavaScript, images

---

## Final note

This project was built to give daily‑wage workers a fair, transparent tool that works in their own language, without any barriers. It demonstrates how free AI and open‑source mapping can solve real problems for underserved communities.
