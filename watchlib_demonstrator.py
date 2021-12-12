import streamlit as st
import streamlit.components.v1 as components
from watchlib import plot
from watchlib.analysis.ecg_analysis import bpm, hrvs
from watchlib.animation import WorkoutAnimation, ECGAnimation
from watchlib.data_handler import DataLoader, CacheHandler, BBoxFilter, BBox
from watchlib.utils import ECG
from watchlib.analysis import heart_rate_variability, bpm
from watchlib.plot import plot_ecg
from datetime import datetime as dt
import matplotlib.pyplot as plt
import os

def header():
    st.write("# Watchlib Demo")
    st.write("**Example path:**")
    st.write("*/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export*")

def set_selected_route():
    st.session_state.selected_route = [route for route in st.session_state.all_routes if route.name == st.session_state.route_option][0]

def set_selected_country():
    st.session_state.selected_bbox = BBoxFilter.countries[st.session_state.country_option]


def start():

    header()
    
    st.sidebar.write("## Export path:")
    st.session_state.health_path = st.sidebar.text_input("Path to Health Export", value="/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")
    st.session_state.cached_route_animations_path = st.session_state.health_path + "/workout-routes/cached_animations"
    #st.session_state.cached_ecg_animations_path = ""
    dl = DataLoader(st.session_state.health_path)
    ch = CacheHandler(st.session_state.health_path)
    st.sidebar.write("## Workout Route Data")

    if "all_routes" not in st.session_state:
        if st.sidebar.button("Load workout data"):
                routes = ch.load_cached_routes()
                st.session_state.all_routes = routes
                st.sidebar.success(str(len(routes)) + " routes have been loaded.")


    with st.sidebar.expander("Filters"):

        if "all_routes" in st.session_state:
            st.selectbox(
                "Select a country", 
                (BBoxFilter.countries.keys()), 
                key="country_option", 
                on_change=set_selected_country
            )

            st.session_state.selected_bbox = BBoxFilter.countries[st.session_state.country_option]
            st.session_state.c_filtered_routes = BBoxFilter(st.session_state.all_routes).filter(st.session_state.selected_bbox)
            
            st.checkbox(
                "Filter out small routes", 
                value=True, 
                key="filter_small_routes"
            )
            
            if st.session_state.filter_small_routes:
                if "selected_bbox" in st.session_state:
                    st.slider(
                        "Diagonal distance of bbox", 
                        min_value = float(BBoxFilter(st.session_state.c_filtered_routes).min_bbox()),
                        max_value = float(BBoxFilter(st.session_state.c_filtered_routes).max_bbox()),
                        value = 1.0,
                        step = 0.5, 
                        key="filter_distance"
                    )
        else:
            st.write("Load the data to apply filters.")



    if "c_filtered_routes" in st.session_state:

        if st.session_state.filter_small_routes:
            bigger_routes = BBoxFilter(st.session_state.c_filtered_routes).filter_small_routes(tolerance=st.session_state.filter_distance)
            st.session_state.cs_filtered_routes = bigger_routes
        
            st.sidebar.selectbox(
                'Select a route',
                ([route.name for route in st.session_state.cs_filtered_routes]), 
                key = "route_option", 
                on_change = set_selected_route
            )
        else:
            st.sidebar.selectbox(
                'Select a route',
                ([route.name for route in st.session_state.cs_filtered_routes]), 
                key = "route_option", 
                on_change = set_selected_route
            )

        
        route = [route for route in st.session_state.all_routes if route.name == st.session_state.route_option][0]
        st.session_state.selected_route = route

    if "selected_route" in st.session_state:
        st.write("## Workout Animation")

        st.session_state.save_animation = st.checkbox("Save animation for faster loading times")
        if st.button("Start workout animation"):
            with st.spinner("Rendering workout route..."):

                if os.path.exists(st.session_state.health_path + "/workout-routes/cached_animations/" + st.session_state.selected_route.name + ".html"):
                    with open(st.session_state.health_path + "/workout-routes/cached_animations/" + st.session_state.selected_route.name + ".html", "r") as f:
                        st.session_state.route_html = f.read()
                else:
                    wa = WorkoutAnimation(st.session_state.selected_route)
                    wa.set_fig_size(shape=(6,6))
                    ani = wa.animate()
                    html = ani.to_jshtml()
                    st.session_state.route_html = html
                components.html(st.session_state.route_html, height=800)
    
            if "route_html" in st.session_state and st.session_state.save_animation and not os.path.exists(st.session_state.health_path + "/workout-routes/cached_animations/" + st.session_state.selected_route.name + ".html"):
                filename = st.session_state.selected_route.name + ".html"
                with open(st.session_state.health_path + "/workout-routes/cached_animations/" + filename, "w") as f:
                    f.write(st.session_state.route_html)
                st.write("Cached animation: *" + filename + "*")

    # ECG
    st.sidebar.write("## ECG Data")
    if "ecgs" not in st.session_state:    
        if st.sidebar.button("Load electrocardiogram data"):
            st.session_state.ecgs = dl.load_ecgs()
            st.sidebar.success(str(len(st.session_state.ecgs)) + " ecgs have been loaded.")

    def set_selected_ecg():
        st.session_state.selected_ecg = [ecg for ecg in st.session_state.ecgs if ecg.name == st.session_state.ecg_option][0]

    if "ecgs" in st.session_state:
        st.sidebar.selectbox('Select an ECG', [ecg.name for ecg in st.session_state.ecgs], key="ecg_option", on_change=set_selected_ecg)     
        ecg = [ecg for ecg in st.session_state.ecgs if ecg.name == st.session_state.ecg_option][0]
        st.session_state.selected_ecg = ecg

    if "ecgs" in st.session_state:
        st.write("## ECG Plot")
        if st.button("Plot ECG"):
            if st.session_state.selected_ecg is None:
                    st.error("Please specify a health path in the sidebar first.")
            else:
                bpm_num = bpm(st.session_state.selected_ecg)
                fig = plot_ecg(st.session_state.selected_ecg)
                hrv = heart_rate_variability(st.session_state.selected_ecg)
                
                st.session_state.ecg_fig = fig
                st.write("Heartbeats per minute: " + str(round(bpm_num)))
                st.write("Heartrate variability: " + str(round(hrv, 2)))
                st.write(st.session_state.ecg_fig)

    if "ecg_fig" in st.session_state:
        st.session_state.plot_path = st.text_input("Path to save plot", "/Users/macbookpro/Desktop/Plots and animations")
        if st.button("Save plot"):
            filename = "plot_" + str(dt.now().timestamp()) + ".png"
            st.session_state.ecg_fig.savefig(st.session_state.plot_path + "/" + filename, dpi=300)
            st.write("Saved plot: *" + filename + "*")

    # Other health data
    st.sidebar.write("## Health Data")
    if "data" not in st.session_state:
        if st.sidebar.button("Load health data"):
                data = ch.load_cached_export_data()
                st.session_state.data = data
                st.sidebar.success(str(len(list(data.keys()))) + " dataframes have been loaded.")

    def set_selected_data():
        st.session_state.selected_data = st.session_state.data[st.session_state.data_option]

    if "data" in st.session_state:
        st.sidebar.selectbox('Select a key', list(st.session_state.data.keys()), key="data_option", on_change=set_selected_data)     
        selected_data = st.session_state.data[st.session_state.data_option]
        st.session_state.selected_data = selected_data

    if "data" in st.session_state:    
        st.write("## Health Data")
        if st.button("Show dataframe"):
            if st.session_state.selected_data is None:
                    st.error("Please specify a health path in the sidebar first.")
            else:
                st.write(st.session_state.selected_data)

if __name__ == "__main__":
    start()