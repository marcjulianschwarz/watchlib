# apple-health-analyser
Python module which helps analyzing apple health data.
Feature:
- Data loader
- Data plotting
- Data analysis

## Get data from health export
To use this Python package you first have to export the health data:

1. Open *Health* app
2. Open your profile in the upper right corner
3. Scroll down
4. Tap on "Export all health data"
5. Confirm that you want to export all health data
6. Wait until the export has finished (this might take some minutes)
7. Select "Save in files"
8. Choose a folder and tap "Save"
9. Last step is to unzip the "Export.zip" file

## Demos
- [DataLoader Demo]()
- [Workout Route Demo]()
- [Electrocardiogram Demo]()

## Workout

3D plot for one workout or rotating animation.
```
workout_three_d: 
    (
        workout_route: DataFrame, 
        color_on: str = "elevation", 
        resolution=0.5, 
        save_animation: bool = False, 
        path: str = "animations/", 
        format: str = "gif"
    ) -> None
```


![animation1634391134 250754](https://user-images.githubusercontent.com/67844154/137590383-b759f12b-6a50-422c-b029-9c0c24505e66.gif)




