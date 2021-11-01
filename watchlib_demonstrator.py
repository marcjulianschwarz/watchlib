import streamlit as st
import streamlit.components.v1 as components
from watchlib.animation import WorkoutAnimation, ECGAnimation
from watchlib.data_handler import DataLoader, BBoxFilter, BBox
from datetime import datetime as dt

def header():
    st.write("# Watchlib Demo")
    st.write("**Example path:**")
    st.write("/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")

def set_selected_route():
    st.session_state.selected_route = st.session_state.all_routes[st.session_state.route_option]

def set_selected_country():
    st.session_state.selected_bbox = BBoxFilter.countries[st.session_state.country_option]


def start():

    header()
    
    st.sidebar.write("## Export path:")
    st.session_state.health_path = st.sidebar.text_input("Path to Health Export", value="/Users/macbookpro/Documents/Code/watchlib/data/apple_health_export")
    st.sidebar.write("## Workout Route Data")

    if "all_routes" not in st.session_state:
        if st.sidebar.button("Load workout data"):
                dl = DataLoader(st.session_state.health_path)
                routes = dl.load_cached_routes()
                st.session_state.all_routes = routes
                st.sidebar.success(str(len(routes.keys())) + " routes have been loaded.")


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
                (st.session_state.cs_filtered_routes.keys()), 
                key = "route_option", 
                on_change = set_selected_route
            )
        else:
            st.sidebar.selectbox(
                'Select a route',
                (st.session_state.c_filtered_routes.keys()), 
                key = "route_option", 
                on_change = set_selected_route
            )

        
        route = st.session_state.all_routes[st.session_state.route_option]
        st.session_state.selected_route = route


    if "selected_route" in st.session_state:
        st.write("## Workout Animation")

        if st.button("Start workout animation"):
            with st.spinner("Rendering workout route..."):
                wa = WorkoutAnimation(st.session_state.selected_route)
                wa.set_fig_size(shape=(6,6))
                ani = wa.animate()
                f = open("/Users/macbookpro/Documents/Code/watchlib/animations/animation_" + str(dt.now().timestamp()) + ".html", "w")
                f.write(ani.to_jshtml())
                f.close()
                components.html(ani.to_jshtml(), height=1000)





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




    if "ecgs" in st.session_state:
        st.write("## ECG Plot")
        if st.button("Plot ECG"):
            if st.session_state.selected_ecg is None:
                    st.error("Please specify a health path in the sidebar first.")
            else:
                data, meta_data = st.session_state.selected_ecg
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