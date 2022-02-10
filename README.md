# watchlib
*watchlib* is a python module for loading, analyzing and visualizing Apple Watch health data.
A detailed documentation can be found in the [Wiki](https://github.com/marcjulianschwarz/watchlib/wiki). To see the module in action you can try out the [watchlib demonstrator](https://github.com/marcjulianschwarz/watchlib/tree/main/demonstrator) or look at some of the [demo notebooks](https://github.com/marcjulianschwarz/watchlib/tree/main/demos).

**Disclaimer:** This is still a work in progres! If you want to help with further development feel free to join me on [Discord](https://discord.gg/TYmZkn9ezf) where we can discuss together or write an [Issue](https://github.com/marcjulianschwarz/watchlib/issues/new) here on GitHub.


## How to export Apple Watch health data
To use this Python package you first have to export the health data like this:

1. Open *Health* app
2. Open your profile in the upper right corner
3. Scroll down
4. Tap on "Export all health data"
5. Confirm that you want to export all health data
6. Wait until the export has finished (this might take some minutes)
7. Select "Save in files"
8. Choose a folder and tap "Save"
9. Last step is to unzip the "Export.zip" file


## ECG
### ECG Analysis

Calculate various heart rate metrics from a 30 second ECG:
- beats per minute (bpm)
- time between heartbeats in ms
- heart rate variability (hrv)
- *coming soon*: ECG wave detection

### ECG Plotting and Animation
- plot ECG
- plot ECG together with metrics
- animate ECG

## Workout Route
Filtering workout routes by:
- country
- bounding box size in km
- length of workout in min

3D animation of workout routes:
- coloring based on:
    - elevation
    - speed
    - course
    - horizontal acceleration
    - vertical acceleration

## Other Health Data
- loading and converting other health data

### Analysis of other health data
*coming soon*


## Notebook demos
- [DataLoader Demo](https://github.com/marcjulianschwarz/watchlib/blob/main/demos/01%20-%20DataLoader.ipynb)
- [Workout Route Demo](https://github.com/marcjulianschwarz/watchlib/blob/main/demos/02%20-%20Workout%20Route.ipynb)
- [Electrocardiogram Demo](https://github.com/marcjulianschwarz/watchlib/blob/main/demos/03%20-%20Electrocardiogram.ipynb)

## Streamlit demo
![streamlit ecg](https://user-images.githubusercontent.com/67844154/139928737-b6043660-24c3-47d6-9ea5-e54b461c9740.png)
![streamlit workout](https://user-images.githubusercontent.com/67844154/139928829-7f27742e-f3a6-4494-9247-9fb81f79a1e4.png)

## ECG heartbeat calculation
![ECG heartbeat calculation slow](https://user-images.githubusercontent.com/67844154/139928546-002b8fbb-94c2-471b-ac05-b5cf64454b9e.png)
![ECG heartbeat calculation fast](https://user-images.githubusercontent.com/67844154/139928552-d6952176-14b5-4431-a3c6-db7eb893dd22.png)


## Workout Animation
Watch an example workout animation <a href="https://www.marc-julian.de/watchlib/animations/animation_1635878885.729083.html">here</a>

