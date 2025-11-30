from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pytz
import csv
import os

# --- FILE CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MONITOR_CSV = os.path.abspath('/Users/sharathchandrashankar/Downloads/annual_conc_by_monitor_2025 3.csv')
DC_CSV = os.path.abspath('/Users/sharathchandrashankar/Downloads/Data_Centers_Database - Data Centers.csv')
WATER_CSV = os.path.abspath('/Users/sharathchandrashankar/Downloads/final_footprint_dataset.csv')

# --- Global variables ---
MONITOR_DATA = []
WATER_DATA = []

# --- Initialize Flask ---
app = Flask(__name__)
CORS(app)

# --- Helper: Convert concentration to AQI ---
def get_aqi_and_color_proxy(concentration_ppm):
    if concentration_ppm <= 0.054:
        aqi = int(concentration_ppm / 0.054 * 50)
        color = "green"
    elif concentration_ppm <= 0.070:
        aqi = 51 + int((concentration_ppm - 0.055) / (0.070 - 0.055) * 49)
        color = "yellow"
    elif concentration_ppm <= 0.085:
        aqi = 101 + int((concentration_ppm - 0.071) / (0.085 - 0.071) * 49)
        color = "orange"
    elif concentration_ppm <= 0.105:
        aqi = 151 + int((concentration_ppm - 0.086) / (0.105 - 0.086) * 49)
        color = "red"
    else:
        aqi = 201 + int((concentration_ppm - 0.106) / 0.01 * 10)
        color = "purple"
    return max(1, aqi), color

# --- Load AQI monitor data ---
def load_monitor_data():
    global MONITOR_DATA
    MONITOR_DATA = []

    if not os.path.exists(MONITOR_CSV):
        print(f"Monitor CSV not found: {MONITOR_CSV}")
        return

    with open(MONITOR_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("Monitor CSV is empty.")
            return

        try:
            lat_idx = header.index('Latitude')
            lon_idx = header.index('Longitude')
            mean_idx = header.index('Arithmetic Mean')
            site_name_idx = header.index('Local Site Name')
            pollutant_idx = header.index('Parameter Name')
        except ValueError as e:
            print(f"Missing column in monitor CSV: {e}")
            return

        count = 0
        for row in reader:
            try:
                lat = float(row[lat_idx])
                lon = float(row[lon_idx])
                conc = float(row[mean_idx])
                city = row[site_name_idx]
                pollutant = row[pollutant_idx].lower()
                aqi, color = get_aqi_and_color_proxy(conc)
                MONITOR_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "aqi": aqi,
                    "city": city,
                    "color": color,
                    "pollutant": pollutant
                })
                count += 1
            except Exception:
                continue

    print(f"Loaded {count} monitor records.")

# --- Load water footprint data ---
def load_water_data():
    global WATER_DATA
    WATER_DATA = []

    if not os.path.exists(WATER_CSV):
        print(f"Water CSV not found: {WATER_CSV}")
        return

    with open(WATER_CSV, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                lat_str = row.get("lat", "").strip()
                lon_str = row.get("lon", "").strip()
                water_str = row.get("water_footprint", "").strip()

                if not lat_str or not lon_str or not water_str:
                    continue

                lat = float(lat_str)
                lon = float(lon_str)
                water_fp = float(water_str)

                WATER_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "water_footprint": water_fp,
                    "subbasin": row.get("subbasin", ""),
                    "state": row.get("plant_state", "")
                })
                count += 1
            except Exception:
                continue

    print(f"Loaded {count} water footprint records.")

# --- Load all data at startup ---
print("Loading monitor and water data...")
load_monitor_data()
load_water_data()
print("Data loading complete.")

# --- API endpoint: /api/monitors ---
@app.route('/api/monitors', methods=['GET'])
def get_monitors():
    pollutant = request.args.get("pollutant", "all").lower()

    if pollutant == "ozone":
        monitors = [m for m in MONITOR_DATA if "ozone" in m["pollutant"]]
    elif pollutant == "pm":
        monitors = [m for m in MONITOR_DATA if "pm" in m["pollutant"]]
    else:
        monitors = MONITOR_DATA

    # Load data centers dynamically
    data_centers = []
    if os.path.exists(DC_CSV):
        with open(DC_CSV, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    lat_str = row.get("Lat", "").strip()
                    lon_str = row.get("Long", "").strip()
                    if not lat_str or not lon_str:
                        continue
                    lat = float(lat_str)
                    lon = float(lon_str)
                    data_centers.append({
                        "Name": row.get("Name", "N/A"),
                        "City": row.get("City", ""),
                        "State": row.get("State", ""),
                        "lat": lat,
                        "lon": lon,
                        "SizeRank": row.get("SizeRank (numeric)", "")
                    })
                except Exception:
                    continue

    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "monitors": monitors,
        "data_centers": data_centers
    })

# --- NEW: API endpoint for /api/water ---
@app.route('/api/water', methods=['GET'])
def get_water():
    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "points": WATER_DATA
    })

# --- API endpoint: /api/water_fuel ---
@app.route('/api/water_fuel', methods=['GET'])
def get_water_fuel():
    # Example: aggregate WATER_DATA by primary_fuel
    fuel_data = [
        {"primary_fuel": "PUR", "water_footprint": 0},
        {"primary_fuel": "WAT", "water_footprint": 728516.30},
        {"primary_fuel": "WDS", "water_footprint": 73098.11}
    ]
    return jsonify(fuel_data)

# --- Test endpoint ---
@app.route('/test', methods=['GET'])
def test():
    return "Flask is working!"

# --- Main entry ---
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
