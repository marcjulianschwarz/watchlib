> class watchlib.filtering.TimeFilter()

This filter will only select routes which were recorded in a given timeframe and which have a minimum and maximum duration.

```python
from watchlib.filtering import CountryFilter

germany_bbox = CountryFilter.countries["Germany"]
cf = CountryFilter(german_bbox)
```


## Parameters
- **_from** : `dt.datetime=dt.fromtimestamp(0)` 
- **_to** : `dt.datetime=dt.now()` 
- **min_duration_sec** : `int=0` 
- **max_duration_sec** : `int=0` 


## Methods
### Filtering
Use the `filter()` method to filter a list of [[WorkoutRoute]]. Only routes that were recorded after `_from`, before `_to`, with a minimum duration of `min_duration_sec` seconds and a maximum duration of `max_duration_sec` seconds will be selected.

**Parameters**:
- `routes` : `List[WorkoutRoute]` -> [[WorkoutRoute]]

**Returns**: 
- `List[WorkoutRoute]` → [[WorkoutRoute]]

**Usage**:
`routes` is a list of [[WorkoutRoute]] previously loaded using [[DataLoader]] or [[CacheHandler]].
The following filter will only select routes that were recorded after the 23. February 2020 and the routes have to be between 30 minutes and 5 hours long.

```python
from watchlib.filtering import TimeFilter

_from = dt.fromtimestamp(1582450784) # 1582450784 = 23.02.2020
_to = dt.now()
min_duration = 60*30
max_duration = 60*60*5

tf = TimeFilter(_from, _to, min_duration, max_duration)
filtered_routes = tf.filter(routes)

# len(filtered_routes) <= len(routes)
```
