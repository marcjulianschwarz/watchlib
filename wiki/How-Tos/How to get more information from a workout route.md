This *How-To* shows how to get more information from a workout route, e.g. workout start/end, duration, max/min/avg of speed, elevation, vAcc, hAcc and course.

## 1. Load the data
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()
```
-> [[How to load Apple Watch Health data from the export folder]]

## 2. Get a specific route
You can get a specific route by selecting a route from the list of loaded routes that we just created or use the method `dl.load_route("name_of_the_route.gpx")`. For this guide we will use the previously loaded list:
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()
route = routes[0]
```

## 3. Get various metrics for a route

```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()
route = routes[0]

elevation = route.elevation

max_elevation = elevation.max()
min_elevation = elevation.min()
mean_elevation = elevation.mean()
```

## 4. Use the describe method
For a quick overview you can use the `describe()` method which will print the values for:
- count 
- mean
- std (standard deviation)
- min
- 25% (percentile) 
- 50% (percentile) 
- 75% (percentile) 
- max
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()
route = routes[0]

route.elevation.describe()
```


