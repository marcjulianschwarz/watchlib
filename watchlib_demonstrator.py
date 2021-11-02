import streamlit as st
import streamlit.components.v1 as components
from watchlib.animation import WorkoutAnimation, ECGAnimation
from watchlib.data_handler import DataLoader, BBoxFilter, BBox
from watchlib.utils import ECG
from datetime import datetime as dt

def header():
    st.write("# Watchlib Demo")
    st.write("**Example path:**")
    st.write("/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")

def set_selected_route():
    st.session_state.selected_route = [route for route in st.session_state.all_routes if route.name == st.session_state.route_option][0]

def set_selected_country():
    st.session_state.selected_bbox = BBoxFilter.countries[st.session_state.country_option]


def start():

    header()
    
    st.sidebar.write("## Export path:")
    st.session_state.health_path = st.sidebar.text_input("Path to Health Export", value="/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")
    dl = DataLoader(st.session_state.health_path)
    st.sidebar.write("## Workout Route Data")

    if "all_routes" not in st.session_state:
        if st.sidebar.button("Load workout data"):
                routes = dl.load_cached_routes()
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

        if st.button("Start workout animation"):
            with st.spinner("Rendering workout route..."):
                wa = WorkoutAnimation(st.session_state.selected_route)
                wa.set_fig_size(shape=(6,6))
                ani = wa.animate()
                html = ani.to_jshtml()
                f = open("/Users/macbookpro/Documents/Code/watchlib/animations/animation_" + str(dt.now().timestamp()) + ".html", "w")
                f.write(html)
                f.close()
                components.html(html, height=1000)



    # ECG

    st.sidebar.write("## ECG Data")
    if "ecgs" not in st.session_state:    
        if st.sidebar.button("Load electrocardiogram data"):
            st.session_state.ecgs = dl.load_ecgs()
            st.sidebar.success(str(len(st.session_state.ecgs)) + " ecgs have been loaded.")

    def set_selected_ecg():
        st.session_state.selected_ecg = st.session_state.ecgs[st.session_state.ecg_option]

    if "ecgs" in st.session_state:
        st.sidebar.selectbox('Select an ECG', (st.session_state.ecgs.keys()), key="ecg_option", on_change=set_selected_ecg)     
        ecg = st.session_state.ecgs[st.session_state.ecg_option]
        st.session_state.selected_ecg = ecg

    if "ecgs" in st.session_state:
        st.write("## ECG Plot")
        if st.button("Plot ECG"):
            if st.session_state.selected_ecg is None:
                    st.error("Please specify a health path in the sidebar first.")
            else:
                e = ECG(st.session_state.selected_ecg)
                bpm, fig = e.bpm(plot=True)
                st.write("Heartbeats per minute: " + str(bpm))
                st.write(fig)


if __name__ == "__main__":
    start()