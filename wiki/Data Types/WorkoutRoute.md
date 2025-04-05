> class watchlib.utils.WorkoutRoute

This is the data type for all workout routes. You can use it to access all properties of a route.

```python
from watchlib.data_handler import DataLoader

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()
route = routes[0]

route.start # -> dt.datetime of when the route started
route["speed"] # or route.speed -> pd.Series with speed data 
```

## Parameters:
- **data** : pd.DataFrame or ET.Element
- **name** : str

## Properties:
- **route** : pd.DataFrame
- **name** : str
- **start** : dt.datetime
- **end** : dt.datetime
- **duration_sec** : float
- **lon** : pd.Series
- **lat** : pd.Series
- **time** : pd.Series
- **elevation** : pd.Series
- **speed** : pd.Series
- **course** : pd.Series
- **hAcc** : pd.Series
- **vAcc** : pd.Series

