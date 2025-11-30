# app.py
import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium import plugins
from streamlit_folium import st_folium

# -------------------------
# Helpers & Data
# -------------------------
def get_aqi_color(aqi):
    """Return hex color for Folium based on AQI."""
    if aqi <= 50:
        return '#00A651'      # Green
    elif aqi <= 100:
        return '#FFE600'      # Yellow
    elif aqi <= 150:
        return '#FF7E00'      # Orange
    elif aqi <= 200:
        return '#C80000'      # Red
    else:
        return '#800080'      # Purple

@st.cache_data
def load_air_quality_data(num_points: int = 500):
    """Generates mock air quality data points focused on the US region."""
    np.random.seed(42)
    min_lat, max_lat = 30, 50
    min_lon, max_lon = -125, -75

    lats = np.random.uniform(min_lat, max_lat, num_points)
    lons = np.random.uniform(min_lon, max_lon, num_points)
    aqi = np.random.normal(loc=90, scale=40, size=num_points).clip(min=10, max=300).astype(int)

    data = pd.DataFrame({
        'lat': lats,
        'lon': lons,
        'AQI': aqi,
        'PM2.5': (aqi * 0.4 + np.random.normal(0, 5, num_points)).clip(min=0, max=100),
        'PM10': (aqi * 0.6 + np.random.normal(0, 10, num_points)).clip(min=0, max=200),
        'Ozone': (aqi * 0.3 + np.random.normal(0, 8, num_points)).clip(min=0, max=150),
        'Monitor_Name': [f'Monitor {i+1} ({lons[i]:.2f}, {lats[i]:.2f})' for i in range(num_points)]
    })

    data['color'] = data['AQI'].apply(get_aqi_color)
    return data

# -------------------------
# Streamlit UI
# -------------------------
def main():
    st.set_page_config(page_title="Interactive Map of Air Quality", layout="wide", initial_sidebar_state="expanded")
    df = load_air_quality_data()

    # --- CSS (dark theme + header) ---
    st.markdown("""
    <style>
        .stApp { background-color: #1a1a1a; color: white; }
        .header-bar { background-color: #004d99; color: white; padding: 10px 20px; display:flex;
                      justify-content:space-between; align-items:center; }
        .airnow-logo { font-size: 24px; font-weight: bold; color: #ffcc00; }
        .airnow-title { font-size: 20px; font-weight: 500; flex-grow: 1; text-align:center; }
        .nav-bar { background-color: #005a9c; color:white; padding:5px 20px; display:flex; gap:20px; }
        .nav-item.active { background-color:#004d99; border-radius:4px; padding:5px; }
        [data-testid="stSidebar"] { background-color: #242424 !important; color: white; }
        .sidebar-group-header { font-size:1.05rem; font-weight:bold; margin-top:12px; color:#ffcc00; padding-bottom:4px; border-bottom:2px solid #333; }
        [data-testid="stHeader"] { display:none; }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="header-bar">
      <div><span style="font-size:24px; font-weight:bold;">Air</span><span class="airnow-logo">Now</span></div>
      <div class="airnow-title">Interactive Map of Air Quality</div>
      <div><div style="background:#222;color:#fff;padding:6px 10px;border-radius:4px">Info</div></div>
    </div>
    <div class="nav-bar">
      <div class="nav-item active">Current</div>
      <div class="nav-item">Forecast</div>
      <div class="nav-item">Loops</div>
      <div class="nav-item">Archive</div>
    </div>
    """, unsafe_allow_html=True)

    # Top-right UI mock
    st.markdown("""
    <div style="position:absolute; top:90px; right:15px; z-index:1000; display:flex; gap:8px;">
      <div style="background:#333;color:white;padding:6px 10px;border-radius:6px;width:220px;text-align:center">Find address or place</div>
      <div style="background:rgba(36,36,36,0.9);color:white;padding:6px 10px;border-radius:6px">Basemaps ▼</div>
      <div style="background:rgba(36,36,36,0.9);color:white;padding:6px 10px;border-radius:6px">Legend ▼</div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("Map Layer Controls")
        st.markdown('<div class="sidebar-group-header">Monitors (NowCast AQI)</div>', unsafe_allow_html=True)
        show_monitors = st.checkbox("Show monitors", value=True)
        st.subheader("Pollutants to Display:")
        show_ozone_pm = st.checkbox("Ozone + PM2.5 + PM10 (combined)", value=True)
        st.markdown('---')
        st.markdown('<div class="sidebar-group-header">Display Options</div>', unsafe_allow_html=True)
        color_by = st.selectbox("Color by:", ["AQI", "PM2.5", "PM10", "Ozone"], index=0)
        st.markdown('---')
        st.caption("Data simulated — updated Nov 28, 2025")

    # -------------------------
    # Folium Map
    # -------------------------
    us_center = [39.5, -98.35]
    m = folium.Map(
        location=us_center,
        zoom_start=4,
        tiles='CartoDB dark_matter'  # dark navy theme
    )

    if show_monitors:
        for _, row in df.iterrows():
            popup_html = f"""
            <b>{row['Monitor_Name']}</b><br>
            AQI: {row['AQI']}<br>
            PM2.5: {row['PM2.5']:.1f}<br>
            PM10: {row['PM10']:.1f}<br>
            Ozone: {row['Ozone']:.1f}
            """
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=6,
                color=row['color'],
                fill=True,
                fill_color=row['color'],
                fill_opacity=0.9,
                popup=folium.Popup(popup_html, max_width=250)
            ).add_to(m)

    # Optional: add grid-like boundaries using GeoJSON US states (built-in folium)
    folium.TileLayer('cartodbpositron', name='Light Basemap', control=False).add_to(m)
    folium.LayerControl().add_to(m)

    st_folium(m, width=1200, height=700)

    # Footer
    st.markdown("""
    <div style="text-align:right; font-size:0.75rem; color:#aaa; padding:5px 15px;">
        Esri, USGS | Esri, TomTom, Garmin, FAO, NOAA, USGS, EPA, USFWS
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
