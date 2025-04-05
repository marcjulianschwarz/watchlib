> class watchlib.data_handler.CacheHandler(path)

The [[DataLoader]] can take a long time to load when there is a lot of data. For further usage of the loaded data you may want to use a `CacheHandler`. 

```python
from watchlib.data_handler import CacheHandler

ch = CacheHandler("path/to/apple_health_export")
```

Use the guide "[[How to export Apple Watch health data]]" to determine the correct path. 

## Parameters
- **path** : str
## Methods
### Caching routes
You can cache routes using the `cache_routes()` method.

**Parameters**:
- `routes` : `List[WorkoutRoute]`

**Usage**:
```python
from watchlib.data_handler import CacheHandler, DataLoader 

path = "path/to/apple_health_export"
dl = DataLoader(path)
ch = CacheHandler(path)

routes = dl.load_routes()
ch.cache_routes(routes)
```

---

### Caching health data
You can cache health data using the `cache_health_data()` method.

**Parameters**:
- `data` : `dict`

**Usage**:
```python
from watchlib.data_handler import CacheHandler, DataLoader 

path = "path/to/apple_health_export"
dl = DataLoader(path)
ch = CacheHandler(path)

health_data = dl.load_health_data()
ch.cache_health_data(health_data)
```

---

### Caching WorkoutAnimation
You can cache a HTML representation of a [[WorkoutAnimation]] using the `cache_route_animation()` method.

**Parameters**:
- `html` : `str`
- `name` : `str`

**Usage**:
```python
from watchlib.data_handler import CacheHandler 

ch = CacheHandler("path/to/apple_health_export")

wa = # ... -> WorkoutAnimation
ani_html = wa.animate().to_jshtml()

ch.cache_route_animation(ani_html, "animation name")
```

---

### Loading routes
You can load routes using the `load_routes()` method. 

**Returns**: 
- `List[WorkoutRoute]` → [[WorkoutRoute]]

**Usage**:
```python
from watchlib.data_handler import CacheHandler 

ch = CacheHandler("path/to/apple_health_export")
routes = ch.load_routes()
```

---

### Loading ECGs
You can load ECGs using the `load_ecgs()` method.

**Returns**: 
- `List[ECG]` → [[ECG]]

**Usage**:
```python
from watchlib.data_handler import CacheHandler 

ch = CacheHandler("path/to/apple_health_export")
ecgs = ch.load_ecgs()
```

---

### Loading health data
You can load health data using the `load_health_data()` method. The keys in the returned dictionary correspond to HealthKitIdentifiers. For a list of all available identifiers visit the Apple Swift Documentation.

**Returns**: 
- `Dict[str, pd.DataFrame]`

**Usage**:
```python
from watchlib.data_handler import CacheHandler 

ch = CacheHandler("path/to/apple_health_export")
health_data = ch.load_health_data()
```

---

### Loading WorkoutAnimation
You can load a HTML representation of a [[WorkoutAnimation]] using the `load_route_animation()` method.

**Parameters**:
- `name` : `str`

**Returns**:
- `str`

**Usage**:
```python
from watchlib.data_handler import CacheHandler 

ch = CacheHandler("path/to/apple_health_export")

ani_html = ch.load_route_animation("animation name")
```

## Utility Methods
### Deleting caches
The `CacheHandler` features several ways to delete caches:

#### Deleting all caches
- `ch.delete_all_caches()`
- `ch.delete_all_health_data_caches()`
- `ch.delete_all_route_caches()`
- `ch.delete_all_animation_caches()`

#### Deleting individual caches
- `ch.delete_health_data_cache()`
- `ch.delete_route_cache()`
- `ch.delete_animation_cache()`

### Check if data is cached 

To check whether routes or health data has been cached use the `isCached()` method.

**Parameters**:
- `data` : str (one of `"routes", "health"`)

**Returns**:
- `bool`

