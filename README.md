
# Environmental Risk Around US Data Centers

An interactive web application that visualizes the environmental impact of data centers across the United States. The app combines **air quality**, **water footprint**, **power consumption**, and **carbon emissions** with **data center locations** to help users explore how digital infrastructure interacts with local environmental conditions.

View it here: https://data-center-map-nu1d.onrender.com/

---
## What this Project does

This project is an exploratory visualization tool designed to analyze indirect environmental impacts associated with data center electricity demand across the United States.

The application does not measure emissions, water use, or air pollution directly from individual data centers. Instead, it visualizes impacts derived from regional electricity generation and supporting infrastructure that supply power to data centers.

The goal is to support comparative analysis, spatial exploration, and scenario reasoning, rather than causal attribution or forecasting.

---

## Key Definitions and Data Interpretation 

Power (Electricity Consumption)
Estimated electricity demand attributed to data center operations and supplied by regional power grids.

Carbon Footprint
CO₂-equivalent emissions associated with electricity generation used by data centers, calculated using grid-level carbon intensity factors.

Water Footprint
Water consumed by power generation and cooling processes required to supply electricity to data centers.

Air Quality (AQI)
Ambient air quality conditions (PM2.5, Ozone) near data center regions, based on public monitoring data. AQI values provide environmental context and are not direct emissions from data centers.

Important: All metrics represent indirect, upstream impacts from electricity generation, not on-site data center measurements.

---

## Features

### 🌫️ Air Quality Layer (Air)

- Visualizes **Air Quality Index (AQI)** conditions across the United States using monitored pollutants:
  - Ozone  
  - PM2.5  
  - Combined “Ozone and PM2.5”
- **Two viewing modes**:
  - **Plot by Facility** – individual monitoring stations as colored points  
  - **Plot by State Average** – each state filled with its average AQI for quick regional comparison
- **Interactions**:
  - Hover hotspots to see AQI values  
  - Use the **Monitor Layer** panel to switch between Ozone + PM2.5, Ozone only, and PM2.5 only  
  - Zoom and pan to inspect pollution around specific data centers  

---

### 💧 Water Footprint Layer (Water)

- Shows **water footprint (m³/MWh)** associated with the electricity and cooling requirements of data centers  
- Marker **color and size** represent the intensity of water usage  
- **View options (top-right filters)**:
  - **State** – focus on all states (default) or a selected state  
  - **Fuel** – filter by electricity source (e.g., natural gas, coal, hydro, solar)  
  - **PCA** – group impacts by power control areas (regional electricity supply zones)  
  - **Plot by Facility** – individual facilities sized/colored by impact  
  - **Plot by State Average** – states colored by average water footprint  
- **More Insights panel**:
  - **Best vs Worst Water Projections** – how future footprint changes under efficient vs inefficient practices  
  - **Fuel Type Breakdown** – which electricity sources drive the highest water consumption  

---

### ⚡ Power Consumption Layer (Power)

- Visualizes **total electricity consumption (MWh)** by power facilities feeding data centers  
- Color and circle size indicate magnitude of power usage  
- **View options** (same control scheme as Water):
  - State / Fuel / PCA filters  
  - Plot by Facility vs Plot by State Average  
- **Tooltips** on hover show:
  - Power consumption (MWh)  
  - Primary fuel type  
  - Regional sub-basin supplying electricity  

---

### 🌍 CO₂ Emissions Layer (CO2)

- Maps **carbon emissions (kg/MWh)** from electricity used by data centers  
- Uses a heat-style color scale (low → high CO₂ intensity)  
- **View options**:
  - Filter by **State**, **Fuel**, and **PCA**  
  - Toggle between facility-level view and state-level averages  
- **Tooltips** on hover show:
  - Emissions intensity (kg/MWh)  
  - Regional sub-basin  
  - Primary generation fuel  
- **More Insights panel**:
  - **Best vs Worst Carbon Projections** – scenario analysis of decarbonization vs business-as-usual  
  - **Fuel Type Contribution** – CO₂ emissions contribution by electricity source  

---

### 🏢 Data Centers Summary
 
- This view shows aggregated charts of:
  - Status breakdown  
  - State distribution  
  - Operator distribution  
  - Size buckets  

---

## Tech Stack

**Frontend**

- Plain HTML, CSS, and JavaScript (single-page app in `app.html`)  
- [Leaflet](https://leafletjs.com/) for interactive mapping and layers  
- [Tailwind CSS](https://tailwindcss.com/) + [DaisyUI](https://daisyui.com/) for UI styling  
- [Chart.js](https://www.chartjs.org/) for summary and “More Insights” charts  

**Backend**

- [Flask](https://flask.palletsprojects.com/) web framework  
- [flask-cors](https://flask-cors.readthedocs.io/) for CORS handling  
- [gunicorn](https://gunicorn.org/) for production serving (via `Procfile`)  

**Data & Processing**

- CSV data files for monitors and environmental metrics (e.g., AQI, water footprint, power usage)  
- [pandas](https://pandas.pydata.org/) and [NumPy](https://numpy.org/) for preprocessing and aggregation  
- Timezone handling via `pytz`  

---

## Getting Started (Local Development)

Clone the repository:

```bash
git clone https://github.com/sharashankr/data-center-map.git
cd data-center-map
````

Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend server:

```bash
python backend.py
```

Backend will start on:

```text
http://127.0.0.1:5000
```

Open the frontend:

**Option A – Served from Flask (if configured)**

```text
http://127.0.0.1:5000/
```

**Option B – Serve app.html statically**

```bash
python -m http.server 8000
```

Then visit:

```text
http://127.0.0.1:8000/app.html
```

Make sure the frontend API URLs match your backend environment (local vs deployed).

---

## Data Sources

**Current Impacts:**

* Electricity, Water & Carbon:
The Environmental Footprint of Data Centers in the United States (Virginia Tech)
https://data.lib.vt.edu/articles/dataset/The_environmental_footprint_of_data_centers_in_the_United_States/14504913
These datasets provide estimates of electricity consumption, water usage, and carbon emissions for U.S. data centers and form the basis of the static impact analyses used in this project.

* Air Quality:
AirNow (U.S. EPA)
https://www.airnow.gov/
AQI data is used to represent ambient air quality conditions (e.g., PM2.5 and Ozone) in regions surrounding data center locations.

**Future Projections (Carbon and Water):**

* `dc_impact_summary.csv`
US-AI-Server-Analysis (PEESE Group)
https://github.com/PEESEgroup/US-AI-Server-Analysis
The dc_impact_summary.csv file was generated by computing summary metrics from the outputs of the above repository.


---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.



