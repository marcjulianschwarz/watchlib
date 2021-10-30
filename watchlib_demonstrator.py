from attr import s
import streamlit as st
import streamlit.components.v1 as components
from watchlib.animation import WorkoutAnimation, ECGAnimation
from watchlib.data_handler import DataLoader
import random

def start():

    st.write("# Watchlib Demo")
    st.write("**Example path:**")
    st.write("/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")
    
    st.sidebar.write("## Export path:")
    st.session_state.health_path = st.sidebar.text_input("Path to Health Export", value="/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")
    dl = DataLoader(st.session_state.health_path)
    
    st.sidebar.write("## Workout Route Data")

    if "routes" not in st.session_state:
        if st.sidebar.button("Load workout data"):
                routes = dl.load_workout_routes_from_csv("/Users/macbookpro/Documents/Code/watchlib/data/cached_routes")
                st.session_state.routes = routes
                st.sidebar.success(str(len(routes.keys())) + " routes have been loaded.")

    def set_selected_route():
        st.session_state.selecte_route = st.session_state.routes[st.session_state.route_option]

    if "routes" in st.session_state:
        sx = st.sidebar.selectbox('Select a route', (st.session_state.routes.keys()), key="route_option", on_change=set_selected_route)     
        route = st.session_state.routes[st.session_state.route_option]
        st.session_state.selected_route = route


    st.sidebar.write("## ECG Data")
    if "ecgs" not in st.session_state:    
        if st.sidebar.button("Load electrocardiogram data"):
            ecgs = dl.load_ecgs()
            st.session_state.ecgs = dl.read_ecgs(ecgs)
            st.sidebar.success(str(len(ecgs)) + " ecgs have been loaded.")

    def set_selected_ecg():
        st.session_state.selected_ecg = st.session_state.ecgs[st.session_state.ecg_option]

    if "ecgs" in st.session_state:
        sx = st.sidebar.selectbox('Select an ECG', (st.session_state.ecgs.keys()), key="ecg_option", on_change=set_selected_ecg)     
        ecg = st.session_state.ecgs[st.session_state.ecg_option]
        st.session_state.selected_ecg = ecg


    if "routes" in st.session_state:
        st.write("## Workout Animation")
        if st.button("Start workout animation"):
            if st.session_state.selected_route is None:
                st.error("Please specify a health path in the sidebar first.")
            else:
                with st.spinner("Rendering workout route..."):
                    wa = WorkoutAnimation(st.session_state.selected_route)
                    wa.set_dpi(80)
                    wa.set_interval(20)
                    wa.set_fig_size(shape=(6,6))
                    ani = wa.animate()
                    components.html(ani.to_jshtml(), height=1000)

    if "ecgs" in st.session_state:
        st.write("## ECG Plot")
        if st.button("Plot ECG"):
            if st.session_state.selected_ecg is None:
                    st.error("Please specify a health path in the sidebar first.")
            else:
                meta_data, data = st.session_state.selected_ecg
                ew = ECGAnimation(data, meta_data)
                fig, ax = ew.plot_ecg()
                st.write(fig)


    # Upload test
    # files = st.file_uploader("Upload health data.", accept_multiple_files=True)
    # if files:
    #     for file in files:
    #         st.write("filename:", file.name)

if __name__ == "__main__":
    start()