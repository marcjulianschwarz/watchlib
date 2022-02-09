
# DataLoader
> class watchlib.data_handler.DataLoader(path)

The easiest way to load Apple Watch data into a usable format in watchlib is to use the `DataLoader`.

```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
```

## Parameters:
- **path** : str
## Methods
### Loading routes
You can load routes using the `load_routes()` method. The returned routes have been loaded from the `.gpx` files.
It defaults to loading routes in parallel. To instead load routes in sequence you can set the `parallel` parameter to `False`. For a small count of routes it might be faster to load them sequentially.

**Parameters**:
- `parallel=True` : bool

**Returns**: 
- `List[WorkoutRoute]` → [[WorkoutRoute]]

**Usage**:
```python
from watchlib.data_handler import DataLoader 

dl = DataLoader("path/to/apple_health_export")

routes = dl.load_routes(parallel=True) 
routes_seq = dl.load_routes(paralle=False)
```

---

### Loading ECGs
You can load ECGs using the `load_ecgs()` method. The returned ECGs have been loaded from the `.csv` files.

**Returns**: 
- `List[ECG]` → [[ECG]]

**Usage**:
```python
from watchlib.data_handler import DataLoader 

dl = DataLoader("path/to/apple_health_export")
ecgs = dl.load_ecgs()
```

---

### Loading health data
You can load health data using the `load_health_data()` method. The keys in the returned dictionary correspond to HealthKitIdentifiers. For a list of all available identifiers visit the Apple Swift Documentation.

**Returns**: 
- `Dict[str, pd.DataFrame]`

**Usage**:
```python
from watchlib.data_handler import DataLoader 

dl = DataLoader("path/to/apple_health_export")
health_data = dl.load_health_data()
```


## Utility Methods

### Check for supported data types
`supports()`
