import streamlit as st
import pandas as pd
import pydeck as pdk

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Environmental Impact - Full Screen Map",
                   layout="wide")

# -------------------------
# CSS for full screen map and floating controls
# -------------------------
st.markdown("""
<style>
/* Remove default Streamlit padding */
.block-container {
    padding: 0rem;
    margin: 0rem;
}

/* Make the map container take full viewport height */
.fullscreen-map > div {
    height: 100vh !important;
}

/* Floating control panel */
.floating-panel {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 9999;
    background-color: rgba(255, 255, 255, 0.9);
    padding: 15px;
    border-radius: 8px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Load Data
# -------------------------
DATA_FILE_PATH = "/Users/sharathchandrashankar/Downloads/annual_conc_by_monitor_2025 3.csv"

try:
    df = pd.read_csv(DATA_FILE_PATH)
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

rename_map = {
    'Latitude': 'Latitude',
    'Longitude': 'Longitude',
    'Parameter Name': 'Parameter',
    'Arithmetic Mean': 'MeanConcentration'
}
df = df.rename(columns=rename_map)

for col in ['Latitude', 'Longitude', 'MeanConcentration']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=['Latitude', 'Longitude', 'MeanConcentration'])

# -------------------------
# Floating controls
# -------------------------
st.markdown('<div class="floating-panel">', unsafe_allow_html=True)

st.header("Air Quality Filters")
show_ozone = st.checkbox("Ozone (1 HOUR / 8-HR RUN AVG)", value=True)
show_pm25 = st.checkbox("PM2.5 (Local Conditions)", value=True)
show_pm10 = st.checkbox("PM10 (Standard Conditions)", value=True)

st.markdown('</div>', unsafe_allow_html=True)

selected_params = []
if show_ozone: selected_params.append('Ozone')
if show_pm25: selected_params.append('PM2.5')
if show_pm10: selected_params.append('PM10')

if selected_params:
    pattern = '|'.join(selected_params)
    df_filtered = df[df['Parameter'].str.contains(pattern, case=False, na=False)]
else:
    df_filtered = df.copy()

# -------------------------
# Color scale
# -------------------------
def get_color_from_concentration(param, mean_val):
    if 'PM2.5' in param:
        if mean_val <= 9.0: return [0, 200, 0]
        elif mean_val <= 12.0: return [255, 255, 0]
        elif mean_val <= 15.0: return [255, 165, 0]
        else: return [255, 0, 0]
    if 'Ozone' in param:
        if mean_val <= 0.054: return [0, 200, 0]
        elif mean_val <= 0.070: return [255, 255, 0]
        elif mean_val <= 0.085: return [255, 165, 0]
        else: return [255, 0, 0]
    return [128, 0, 128]

df_filtered['color'] = df_filtered.apply(lambda r: get_color_from_concentration(r['Parameter'], r['MeanConcentration']), axis=1)

# -------------------------
# PyDeck Full Screen Map
# -------------------------
view_state = pdk.ViewState(
    latitude=df_filtered['Latitude'].mean() if not df_filtered.empty else 39.5,
    longitude=df_filtered['Longitude'].mean() if not df_filtered.empty else -98.35,
    zoom=4,
    pitch=0
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_filtered,
    get_position='[Longitude, Latitude]',
    get_fill_color='color',
    get_radius=20000,
    pickable=True,
    auto_highlight=True
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>{Parameter}</b><br>Mean: {MeanConcentration}<br>Site: {Local Site Name}",
        "style": {"color": "white"}
    },
    map_style='mapbox://styles/mapbox/dark-v10'
)

# Full-screen container
st.markdown('<div class="fullscreen-map">', unsafe_allow_html=True)
st.pydeck_chart(deck, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)