This *How-To* shows how to load Apple Watch data from the export folder (-> [[How to export Apple Watch health data]]).

## 1. Import the DataLoader
Import the [[DataLoader]] like this:
```python
from watchlib.data_handler import DataLoader
```

## 2. Create a DataLoader
Create a [[DataLoader]] and pass it the path to your `apple_health_export` folder like this:
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
```

## 3. Load data
### 3.1 Load routes
You can load all of the routes (-> [[WorkoutRoute]]) in `path/to/apple_health_export/workout_routes` using the `load_routes()` method like this:
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()
```

### 3.2 Load ECGs
You can load all of the ECGs (-> [[ECG]]) in `path/to/apple_health_export/electrocardiograms` using the `load_ecgs()` method like this:
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
ecgs = dl.load_ecgs()
```

### 3.3 Load other health data
You can load all other health data in `path/to/apple_health_export/Export.xml` using the `load_health_data()` method like this:
```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
other_health_data = dl.load_health_data()
```