> class watchlib.data_handler.HealthDataHandler(health_data)

The `HealthDataHandler` can be used to preprocess health data (cleaning and grouping).

```python
from watchlib.data_handler import HealthDataHandler

hdh = HealthDataHandler(healthdata)
```

Use the guide "[[How to load Apple Watch Health data from the export folder]]".

## Parameters
- **data** : Dict[str : pd.DataFrame]
## Methods

### Group and Join Data 
You can group and join data for different identifiers using the `group()` method.

**Usage**:
```python
from watchlib.data_handler import HealthDataHandler

hdh = HealthDataHandler(healthdata)
identifiers = hdh..get_quantity_identfiers(types=["sum", "mean"])
grouped_df = hdh.group(identifiers)
```

## Utility Methods

### Loading identifiers 
You can load all identifiers using the `load_identifiers()` method. It returns a JSON object containing all HealthKitIdentifiers. For a list of all available identifiers visit the Apple Swift Documentation.

**Parameters**:
- `parallel=True` : `bool`

**Returns**: 
- JSON object

---

### Get event identifiers 


---

### Get quantity and category identifiers


**Returns**: 
- `Dict[str, pd.DataFrame]`

**Usage**:
```python
from watchlib.data_handler import DataLoader 

dl = DataLoader("path/to/apple_health_export")
health_data = dl.load_health_data()
```

---

### Get data for identifiers


---

### Is identifier compatible with aggregate function
`is_identifier(identifier, aggregate)` where `aggregate` can be `sum` or `mean`.


