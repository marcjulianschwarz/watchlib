> class watchlib.filtering.CountryFilter()

This filter will only select routes which were recorded in the [[BBox]] of a given country.
Currently it only supports the following countries:
- All
- Italy
- Germany
- Austria

More/all countries are coming soon.

```python
from watchlib.filtering import CountryFilter

germany_bbox = CountryFilter.countries["Germany"]
cf = CountryFilter(german_bbox)
```


## Parameters
- **country_bbox** : `BBox` -> [[BBox]]

## Properties
- **countries** : `Dict[str, BBox]` -> [[BBox]] and see supported countries
## Methods
### Filtering
Use the `filter()` method to filter a list of [[WorkoutRoute]] according to `country_bbox`.

**Parameters**:
- `routes` : `List[WorkoutRoute]` -> [[WorkoutRoute]]

**Returns**: 
- `List[WorkoutRoute]` → [[WorkoutRoute]]

**Usage**:
`routes` is a list of [[WorkoutRoute]] previously loaded using [[DataLoader]] or [[CacheHandler]].

```python
from watchlib.filtering import CountryFilter

germany_bbox = CountryFilter.countries["Germany"]
cf = CountryFilter(german_bbox)
filtered_routes = cf.filter(routes)

# len(filtered_routes) <= len(routes)
```
