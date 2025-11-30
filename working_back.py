from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import pytz
import csv
import os

# --- FILE CONFIGURATION ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE_PATH = os.path.abspath('/Users/sharathchandrashankar/Downloads/annual_conc_by_monitor_2025 3.csv')

# Global variable to hold the parsed data
MONITOR_DATA = []

# Initialize Flask
app = Flask(__name__)
CORS(app)


def get_aqi_and_color_proxy(concentration_ppm):
    """Convert Ozone/PM concentration to mock AQI and color"""
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


def load_data_from_csv():
    """Reads CSV and populates MONITOR_DATA with pollutant type"""
    global MONITOR_DATA
    MONITOR_DATA = []

    if not os.path.exists(CSV_FILE_PATH):
        print(f"ERROR: CSV file not found at {CSV_FILE_PATH}. Using empty data.")
        return

    print(f"Loading data from {CSV_FILE_PATH}...")
    with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)

        # Adjust these if your CSV has pollutant type in a column
        try:
            lat_idx = header.index('Latitude')
            lon_idx = header.index('Longitude')
            mean_idx = header.index('Arithmetic Mean')
            site_name_idx = header.index('Local Site Name')
            pollutant_idx = header.index('Parameter Name')  # <- NEW COLUMN
        except ValueError as e:
            print(f"ERROR: Missing required column: {e}")
            return

        for i, row in enumerate(reader):
            try:
                lat = float(row[lat_idx])
                lon = float(row[lon_idx])
                mean_conc = float(row[mean_idx])
                city = row[site_name_idx]
                pollutant = row[pollutant_idx].lower()  # 'ozone' or 'pm2.5'

                aqi, color = get_aqi_and_color_proxy(mean_conc)

                MONITOR_DATA.append({
                    "lat": lat,
                    "lon": lon,
                    "aqi": aqi,
                    "city": city,
                    "color": color,
                    "pollutant": pollutant
                })

            except (ValueError, IndexError):
                continue

    print(f"Successfully loaded {len(MONITOR_DATA)} monitor records.")


# Load data on startup
load_data_from_csv()


# --- API ROUTES ---

@app.route('/api/monitors', methods=['GET'])
def get_monitors():
    """Return monitors, optionally filtered by pollutant"""
    pollutant = request.args.get("pollutant", "all").lower()

    if pollutant == "ozone":
        monitors = [m for m in MONITOR_DATA if "ozone" in m["pollutant"]]
    elif pollutant == "pm":
        monitors = [m for m in MONITOR_DATA if "pm" in m["pollutant"]]
    else:
        monitors = MONITOR_DATA

    return jsonify({
        "timestamp": datetime.now(pytz.utc).isoformat(),
        "monitors": monitors
    })


@app.route('/test', methods=['GET'])
def test():
    return "Flask is working!"


if __name__ == '__main__':
    print(f"Starting Flask server on http://127.0.0.1:3000...")
    app.run(debug=True, port=3000, use_reloader=False)