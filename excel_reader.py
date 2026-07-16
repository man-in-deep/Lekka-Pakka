import openpyxl
from pathlib import Path

def get_map_data():
    """
    Reads 'AP_District_Mandal_Priority.xlsx' from the project root
    (same folder as this script) and returns a list of dicts.
    """
    file_path = Path(__file__).parent / "AP_District_Mandal_Priority.xlsx"
    workbook = openpyxl.load_workbook(file_path)
    sheet = workbook.active

    circles = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        district, mandal, lat, lng, radius_km, priority = row
        if lat is None or lng is None:
            continue
        circles.append({
            "lat": float(lat),
            "lng": float(lng),
            "radius_m": float(radius_km) * 1000,
            "priority": int(priority),
            "district": district,
            "mandal": mandal
        })
    return circles