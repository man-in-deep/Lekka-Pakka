# Lekka-Pakka
---

```markdown
# 🏗️ Lekka-Pakka – Labour Management System  
**A location‑aware, AI‑powered daily‑wage management platform for Indian labourers and contractors**

---

## 📽️ Project Demo Video  
*Watch the full working of the system (click the play button)*  

👉 **[▶️ Watch Demo Video](https://drive.google.com/file/d/YOUR_VIDEO_ID/preview)**  

> **Note:** Replace `YOUR_VIDEO_ID` with the actual ID from your Google Drive video link.  
> You can also embed the video directly using the HTML below (GitHub supports raw HTML in Markdown):  
> ```html
> <iframe src="https://drive.google.com/file/d/YOUR_VIDEO_ID/preview" width="640" height="360" allow="autoplay"></iframe>
> ```
> (If the iframe doesn’t render, the clickable link above works perfectly.)

---

## 🔍 Why This Project? – The Problem  

In Andhra Pradesh, daily‑wage workers (masons, carpenters, sweepers, etc.) often:  
- Have **no formal record** of how much they should be paid.  
- Don’t know the **fair hourly rate** for their trade in their current location.  
- Are paid less by contractors without any proof of the "official" rate.  
- Lack a simple, language‑friendly tool to track their daily earnings.

Contractors, on the other hand, need to quickly estimate labour costs for different trades across different areas (urban Visakhapatnam vs. rural Araku Valley) without calling multiple people.

**Lekka‑Pakka** solves this by:  
✅ Automatically fetching and calculating **location‑based hourly wages** using Google Gemini AI.  
✅ Giving every labourer a **password‑free digital identity** tied to their device.  
✅ Automatically detecting the worker’s location and the “priority” zones (green/yellow/red circles) around them.  
✅ Computing the **correct daily wage** using a transparent, tamper‑proof algorithm.  
✅ Storing every day’s earnings so labourers can **track income and compare** with what the contractor actually paid.

---

## ✨ What Makes It Novel?  

### 1. **Device‑based, password‑less login**  
   - No usernames, no passwords, no OTPs.  
   - The browser generates a **unique, random UUID** (using `crypto.randomUUID()`) and stores it in `localStorage`.  
   - This ID is combined with a prefix (e.g., `contr-` for contractors, `labour-` for labourers).  
   - The same device always gets the **same ID**, even after restarting – no account creation needed.  
   - **Why it’s important:** Most labourers are not tech‑savvy; a “Proceed” button is all they need. Privacy‑friendly, no personal data stored.

### 2. **AI‑powered wage base rates with automatic 15‑day refresh**  
   - The system uses **Google Gemini (free tier)** to fetch the average hourly wage for 32 worker types in Visakhapatnam (Gajuwaka).  
   - From that **single API call per trade**, it derives rates for Ibrahimpatnam (−₹10) and Araku Valley (−₹20) – a realistic spread.  
   - The entire database (96 rows) is **automatically refreshed every 15 days** by a background scheduler.  
   - **Why it’s novel:** No manual data entry, always up‑to‑date. The 15‑day cycle mimics real‑world wage revision periods.

### 3. **Dynamic, location‑based wage calculation**  
   - The map is populated with circles (from an Excel sheet) representing priority zones:  
     🟢 Priority 1 (Green) – urban, higher cost  
     🟡 Priority 2 (Yellow) – semi‑urban  
     🔴 Priority 3 (Red) – rural, lower cost  
   - When a contractor/labourer opens the dashboard, the browser grabs their GPS location and checks which circles they’re inside.  
   - The final wage is **computed in real‑time** using a sophisticated algorithm (see below), taking into account **all intersecting circles**.  
   - **Why it’s novel:** It’s like “surge pricing for labour” – fair, transparent, and automatically adjusted to the worker’s exact location.

### 4. **Transparent, auditable daily earnings**  
   - Labourers see a preview of their day’s pay **before saving** (hours × hourly rate).  
   - They can enter how much the contractor actually gave, and the system stores both the calculated and actual amounts.  
   - A **bar chart** compares calculated vs. received wages over the last 7 days, exposing any shortfalls.  
   - All data is stored in a cloud PostgreSQL database – no paper, no cheating.

### 5. **Fully multilingual (English / తెలుగు / हिन्दी)**  
   - Every button, label, dropdown, and message can be switched instantly on both login and dashboard pages.  
   - Worker types are also translated – e.g., “Carpenter” becomes “వడ్రంగి” in Telugu.  
   - **Why it’s important:** Cuts the language barrier completely for rural labourers.

---

## 🧠 The Wage Calculation Algorithm (Detailed)

The heart of the system is a **location‑priority intersection algorithm** that combines base wages with zone multipliers.

### Step 1 – Get Base Wages from Database
The `workers` table stores 96 rows (32 trades × 3 priorities) with hourly rates fetched from Gemini.  
For a given trade (e.g., Mason) we have:
- Priority 1 (Gajuwaka) rate = `R1`
- Priority 2 (Ibrahimpatnam) rate = `R2`
- Priority 3 (Araku Valley) rate = `R3`

### Step 2 – Detect Intersecting Circles
The user’s GPS coordinates are compared with every circle’s centre and radius using the **Haversine formula** (great‑circle distance).  
A circle is “intersecting” if `distance(user, circle_center) ≤ circle_radius`.

Let `S` be the set of intersecting circles. Each circle has a priority (1, 2, or 3).

### Step 3 – Compute Final Rate

#### Case A – Only one priority present (e.g., only green circles)
- Select the base rate of that priority (e.g., `R1` if all circles are priority 1).
- Add a **bonus**:
  - Green (priority 1): **+20%**
  - Yellow (priority 2): **+15%**
  - Red (priority 3): **+10%**
- Formula: `final = base × (1 + bonus%)`

#### Case B – Multiple priorities present (mixed colours)
1. Collect the base rates for each intersecting circle (using the trade’s rate for that circle’s priority).  
   Example: circles with priorities [1, 2, 1] → base pays = [R1, R2, R1].
2. Compute the **average** of these base pays: `avg = (sum of all collected base pays) / N`
3. For each intersecting circle, add an **extra percentage** based on its priority:
   - Green (priority 1) → add **10% of that circle’s base rate**
   - Yellow (priority 2) → add **7.5% of that circle’s base rate**
   - Red (priority 3) → add **5% of that circle’s base rate**
   - Sum all these extras: `extras = Σ (base_i × extra_percentage_i)`
4. Subtotal = `avg + extras`

#### Final Step – Inflation Adjustment
After the subtotal (from either case), we apply a **5% inflation multiplier**:  
`final_displayed_rate = subtotal × 1.05`

This ensures the rate stays relevant to real‑world price rises.

> **Why this algorithm?**  
> It mimics how actual wage negotiations happen – a base rate adjusted by multiple factors (locality type, demand, inflation). By making it explicit, we remove any ambiguity for both labourer and contractor.

---

## 💻 System Architecture & Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python (Flask) |
| **Database** | PostgreSQL (Neon – serverless, free tier) |
| **AI/ML** | Google Gemini API (free tier, Gemini 2.0 Flash‑Lite) |
| **Maps** | Leaflet.js + OpenStreetMap (free, no API key) |
| **Charts** | Chart.js |
| **Background Jobs** | APScheduler |
| **Excel Parsing** | openpyxl |
| **Deployment** | Render.com (free tier) |

- **Session management** uses Flask’s signed cookies (no database‑stored sessions).  
- **Device IDs** are generated entirely client‑side and stored in `localStorage` – no server‑side password hashing.  
- The Excel file with zone data is read once at app startup and kept in memory for speed.

---

## 🔄 The 15‑Day Refresh Cycle

1. A `date_tracker` table holds the start date of the current cycle.  
2. On app startup and **before every home page request**, the system checks how many days have passed since that date.  
3. If ≥ 15 days, it:
   - Drops the `workers` table.
   - Calls Gemini for 32 trades (only for Visakhapatnam).
   - Derives the other two rates and inserts 96 rows.
   - Updates the start date to today.
4. A background scheduler also runs this check every 24 hours, so the data stays fresh even if nobody visits the site.

**Why 15 days?** It’s long enough to avoid rate‑limit issues (free Gemini tier), and short enough to capture real‑world wage fluctuations (e.g., seasonal changes).

---

## 🗺️ Why Andhra Pradesh? – Context

Andhra Pradesh has a highly mobile labour workforce moving between urban centres (Gajuwaka, Visakhapatnam) and rural hinterlands (Araku Valley). Wages vary drastically:
- A mason in Gajuwaka might earn **₹350–400/hour**.
- The same mason in Araku Valley may get only **₹200–250/hour**.

Contractors often exploit this information gap. This system:
- **Empowers labourers** by showing them the **expected rate for their exact location**.
- **Helps contractors** accurately budget for projects across different mandals without guesswork.
- Creates a **digital paper trail** of earnings, which can serve as proof for minimum‑wage compliance.

The zone data (circles) comes directly from an official‑style Excel sheet (`AP_District_Mandal_Priority.xlsx`) that can be updated by administrators. The colour coding (green/yellow/red) reflects the *priority* of the area – a concept familiar to government schemes.

---

## 🚀 Getting Started (Local Development)

1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Add a `.env` file with:
   ```
   DATABASE_URL=postgresql://...
   GEMINI_API_KEY=your-key
   ```
4. Place your `AP_District_Mandal_Priority.xlsx` in the project root.
5. Run `python app.py` – the app will auto‑create tables and fetch initial wage data.
6. Visit `http://127.0.0.1:5000`.

---

## 📤 Deployment (Free)

Deployed on [Render.com](https://render.com) with:
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- Environment variables set in Render dashboard.
- A free cron‑job (e.g., cron‑job.org) pings the site every 14 minutes to keep it awake.

---

## 🧾 Key Files

| File | Purpose |
|------|---------|
| `app.py` | Flask routes (Admin, Contractor, Labour) |
| `database.py` | All PostgreSQL operations, including 15‑day logic |
| `gemini_service.py` | Calls Gemini API to get base wages |
| `excel_reader.py` | Reads the priority‑zone Excel file |
| `templates/*.html` | Government‑themed UI with Leaflet maps |
| `static/css/style.css` | Tricolor, official fonts, scrollbar styling |
| `static/js/language.js` | Multilingual text switching |

---

## 🧠 Why This Project Stands Out

- **No OTP, no password** – pure device‑based identity.  
- **AI + GIS** combined for hyper‑local wage computation.  
- **Real‑world impact** – built after studying the labour markets of Visakhapatnam, Ibrahimpatnam, and Araku Valley.  
- **Completely open‑source** and free to deploy using entirely free cloud tiers (Neon PostgreSQL, Gemini free API, Render, OpenStreetMap).

---

*Made with ❤️ for the workers of Andhra Pradesh.*
```

---
