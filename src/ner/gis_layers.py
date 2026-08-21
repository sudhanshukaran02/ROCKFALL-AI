import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pydeck as pdk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.ner.config import Config
from src.ner.field_reporting import get_all_field_reports


# ---------------------------------------------------------
# GIS MAP LAYERS & PYDECK INTERACTIVE MAP ENGINE
# ---------------------------------------------------------
def get_verified_landslide_events_df():
    csv_path = os.path.join(Config.BASE_DIR, "data", "ner", "landslide_events_verified.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Filter valid coordinates
        df = df[(df['latitude'].notnull()) & (df['longitude'].notnull())].copy()
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df = df.dropna(subset=['latitude', 'longitude']).reset_index(drop=True)
        return df
    else:
        return pd.DataFrame()


def build_pydeck_gis_map(show_events=True, show_reports=True, show_susceptibility_grid=True):
    """
    Constructs an interactive PyDeck GIS map displaying real verified landslide events,
    submitted prototype field reports, and regional susceptibility centroids.
    """
    layers = []

    # 1. Verified Landslide Events Layer (Red Scatter)
    df_events = get_verified_landslide_events_df()
    if show_events and len(df_events) > 0:
        event_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_events,
            get_position=["longitude", "latitude"],
            get_color="[211, 84, 0, 200]",
            get_radius=8000,
            pickable=True,
            auto_highlight=True
        )
        layers.append(event_layer)

    # 2. Submitted Field Reports Layer (Purple Scatter)
    df_reports = get_all_field_reports()
    if show_reports and len(df_reports) > 0:
        df_rep_valid = df_reports.dropna(subset=['latitude', 'longitude']).copy()
        if len(df_rep_valid) > 0:
            report_layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_rep_valid,
                get_position=["longitude", "latitude"],
                get_color="[142, 68, 173, 230]",
                get_radius=10000,
                pickable=True,
                auto_highlight=True
            )
            layers.append(report_layer)

    # Center map on Shillong / NER coordinates (25.5788 N, 91.8933 E)
    view_state = pdk.ViewState(
        latitude=25.5788,
        longitude=91.8933,
        zoom=6.5,
        pitch=30
    )

    tooltip = {
        "html": "<b>Event / Report Details</b><br/>"
                "<b>State/Type:</b> {state}<br/>"
                "<b>Date/Time:</b> {event_date}<br/>"
                "<b>Location:</b> {location_name}<br/>"
                "<b>Source:</b> {source}",
        "style": {"color": "white", "backgroundColor": "#2c3e50"}
    }

    r_map = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/outdoors-v11"
    )

    return r_map
