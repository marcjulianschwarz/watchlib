import sys
sys.path.append("../")

from watchlib.utils.structs import ECG, WorkoutRoute
import streamlit as st
import streamlit.components.v1 as components
from watchlib.animation import WorkoutAnimation, constants
from watchlib.filtering import CountryFilter, DiagonalBBoxFilter, TimeFilter, FilterPipeline
from watchlib.data_handler import DataLoader, CacheHandler
from watchlib.analysis import heart_rate_variability, bpm
from watchlib.plot import plot_ecg
from datetime import datetime as dt
import os


def header():
    st.write("# Watchlib Demo")    

def set_selected_route():
    st.session_state.selected_route = [
        route for route in st.session_state.all_routes if route.name == st.session_state.route_option][0]


def set_selected_country():
    st.session_state.selected_bbox = CountryFilter.countries[st.session_state.country_option]


def set_selected_ecg():
    st.session_state.selected_ecg = [
        ecg for ecg in st.session_state.ecgs if ecg.name == st.session_state.ecg_option][0]


def set_selected_data():
    st.session_state.selected_data = st.session_state.data[st.session_state.data_option]

def route_sort(route: WorkoutRoute):
    return route.name

def ecg_sort(ecg: ECG):
    return ecg.name

def start():

    header()

    st.sidebar.write("## Export path:")
    st.session_state.health_path = st.sidebar.text_input("Path to Health Export")

    dl = DataLoader(st.session_state.health_path)
    ch = CacheHandler(st.session_state.health_path)

    if st.button("Delete export cache."):
        ch.delete_all_export_caches()
    if st.button("Delete workout route cache."):
        ch.delete_all_route_caches()

    if dl.supports("routes"): 
        st.sidebar.write("## Workout Route Data")

        if "all_routes" not in st.session_state:
            if st.sidebar.button("Load workout data"):
                routes = []
                if ch.isCached("routes"):
                    st.sidebar.info(f"Loading {dl.count_routes()} cached routes. This might take some time.")
                    routes = ch.load_cached_routes()
                else:
                    st.sidebar.info(f"Loading {dl.count_routes()} routes. This might take some time.")
                    routes = dl.load_routes()
                    st.sidebar.info(f"Caching {dl.count_routes()} routes. This might take some time.")
                    ch.cache_routes(routes)
                routes.sort(key=route_sort)
                st.session_state.all_routes = routes
                st.sidebar.success(f"{len(routes)} routes have been loaded.")

        with st.sidebar.expander("BBox Filters"):

            if "all_routes" in st.session_state:
                st.selectbox(
                    "Select a country",
                    (CountryFilter.countries.keys()),
                    key="country_option",
                    on_change=set_selected_country
                )

                st.session_state.selected_country = CountryFilter.countries[
                    st.session_state.country_option]

                st.slider(
                    "Diagonal distance of bbox",
                    min_value=float(0),
                    max_value=float(100),
                    value=1.0,
                    step=0.5,
                    key="filter_distance"
                )

            else:
                st.write("Load the data to apply filters.")

        with st.sidebar.expander("Time Filters"):

            if "all_routes" in st.session_state:
                st.text_input("From", key="_from", value="0")
                st.text_input("To", key="_to", value="1642680802")
                st.slider("Min duration", min_value=float(0), max_value=float(60*60*10), value=0.0, step=1.0, key="min_duration")
                st.slider("Max duration", min_value=float(0), max_value=float(60*60*10), value=float(60*60*10), step=1.0, key="max_duration")

        if "selected_country" in st.session_state and "filter_distance" in st.session_state:

            routes = st.session_state.all_routes
            cf = CountryFilter(st.session_state.selected_country)
            dbf = DiagonalBBoxFilter(st.session_state.filter_distance)
            tf = TimeFilter(dt.fromtimestamp(int(st.session_state._from)), dt.fromtimestamp(int(st.session_state._to)), st.session_state.min_duration, st.session_state.max_duration)

            filter_pipeline = FilterPipeline(
                ["country_filter", "diagonal_bbox_filter", "time_filter"], [cf, dbf, tf])
            filtered_routes = filter_pipeline.filter(routes)
            st.session_state.filtered_routes = filtered_routes

            if "filtered_routes" in st.session_state:

                st.sidebar.selectbox(
                    'Select a route',
                    ([route.name for route in st.session_state.filtered_routes]),
                    key="route_option",
                    on_change=set_selected_route
                )

                st.sidebar.selectbox(
                    'Color on',
                    (constants.WORKOUT_OPTIONS["color_on"]),
                    key="color_on"
                )

            route = [route for route in st.session_state.all_routes if route.name ==
                    st.session_state.route_option]
            if len(route) > 0:
                route = route[0]
                st.session_state.selected_route = route

        if "selected_route" in st.session_state:
            st.write("## Workout Animation")

            st.session_state.save_animation = st.checkbox(
                "Load cached animations if available")
            if st.button("Start workout animation"):
                with st.spinner("Rendering workout route..."):

                    name = f"{st.session_state.selected_route.name}-{st.session_state.color_on}.html"
                    if st.session_state.save_animation and ch.is_animation_cached(name):
                        st.session_state.route_html = ch.load_cached_route_animation(name)
                    else:
                        wa = WorkoutAnimation(st.session_state.selected_route)
                        wa.config.set_fig_size(shape=(6, 6))
                        wa.set_color_on(st.session_state.color_on)
                        ani = wa.animate()
                        html = ani.to_jshtml()
                        st.session_state.route_html = html
                    components.html(st.session_state.route_html, height=800)

                if "route_html" in st.session_state and not ch.is_animation_cached(name):
                    ch.cache_route_animation(st.session_state.route_html, name)
                    st.write(f"Cached animation: *{name}*")

    # ----------
    # ECG
    # ----------
    if dl.supports("ecg"):    
        st.sidebar.write("## ECG Data")
        if "ecgs" not in st.session_state:
            if st.sidebar.button("Load electrocardiogram data"):
                st.session_state.ecgs = dl.load_ecgs()
                st.session_state.ecgs.sort(key=ecg_sort)
                st.sidebar.success(
                    f"{len(st.session_state.ecgs)} ecgs have been loaded.")

        if "ecgs" in st.session_state:
            st.sidebar.selectbox('Select an ECG', [
                                ecg.name for ecg in st.session_state.ecgs], key="ecg_option", on_change=set_selected_ecg)
            ecg = [ecg for ecg in st.session_state.ecgs if ecg.name ==
                st.session_state.ecg_option][0]
            st.session_state.selected_ecg = ecg

        if "ecgs" in st.session_state:
            st.write("## ECG Plot")
            if st.button("Plot ECG"):
                if st.session_state.selected_ecg is None:
                    st.error("Please specify a health path in the sidebar first.")
                else:
                    bpm_num = bpm(st.session_state.selected_ecg)
                    fig = plot_ecg(st.session_state.selected_ecg, return_fig=True)
                    hrv = heart_rate_variability(st.session_state.selected_ecg)

                    st.session_state.ecg_fig = fig
                    st.write(f"Heartbeats per minute: {round(bpm_num, 2)}")
                    st.write(f"Heartrate variability: {round(hrv, 2)}")
                    st.write(st.session_state.ecg_fig)

        if "ecg_fig" in st.session_state:
            st.session_state.plot_path = st.text_input(
                "Path to save plot", "")
            if st.button("Save plot"):
                filename = f"plot_{dt.now().timestamp()}.png"
                st.session_state.ecg_fig.savefig(
                    f"{st.session_state.plot_path}/{filename}", dpi=300)
                st.write(f"Saved plot: *{filename}*")

    # ----------
    # Other health data
    # ----------

    if dl.supports("health"):
        st.sidebar.write("## Health Data")
        if "data" not in st.session_state:
            if st.sidebar.button("Load health data"):
                data = {}
                if ch.isCached("export"):
                    st.sidebar.info(f"Loading cached health dataframes...")
                    data = ch.load_cached_export_data()
                else:
                    st.sidebar.info(f"Loading and Caching health dataframes...")
                    data = dl.load_export_data()
                    ch.cache_export_data(data)
                st.session_state.data = data
                st.sidebar.success(
                    f"{len(list(data))} dataframes have been loaded.")

        if "data" in st.session_state:
            st.sidebar.selectbox('Select a key', list(
                st.session_state.data.keys()), key="data_option", on_change=set_selected_data)
            selected_data = st.session_state.data[st.session_state.data_option]
            st.session_state.selected_data = selected_data

        if "data" in st.session_state:
            st.write("## Health Data")
            if st.button("Show dataframe"):
                if st.session_state.selected_data is None:
                    st.error("Please specify a health path in the sidebar first.")
                else:
                    st.write(f"## {st.session_state.data_option}")
                    st.write(st.session_state.selected_data)


if __name__ == "__main__":
    start()
