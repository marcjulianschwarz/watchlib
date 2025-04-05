> class watchlib.filtering.FilterPipeline()

The `FilterPipeline` can be used to chain multiple filters in a row. It works with every [[Filter]]:
- [[DiagonalBBoxFilter]]
- [[CountryFilter]]
- [[TimeFilter]]

```python
from watchlib.filtering import FilterPipeline, CountryFilter, DiagonalBBoxFilter

cf = CountryFilter(CountryFilter.countries["Germany"])
dbbf = DiagonalBBoxFilter(10)

fp = FilterPipeline(filter_names=["cf", "tf"], filters=[cf, dbbf])
```


## Parameters
- **filter_names** : `List[str]` 
- **filters** : `List[Filter]` -> [[Filter]]

## Methods
### Filtering
Use the `filter()` method to filter a list of [[WorkoutRoute]]. Only routes that were selected by the `filters` will be left.

**Parameters**:
- `routes` : `List[WorkoutRoute]` -> [[WorkoutRoute]]

**Returns**: 
- `List[WorkoutRoute]` → [[WorkoutRoute]]

**Usage**:
`routes` is a list of [[WorkoutRoute]] previously loaded using [[DataLoader]] or [[CacheHandler]].

```python
from watchlib.filtering import FilterPipeline, CountryFilter, DiagonalBBoxFilter

cf = CountryFilter(CountryFilter.countries["Germany"])
dbbf = DiagonalBBoxFilter(10)

fp = FilterPipeline(filter_names=["cf", "tf"], filters=[cf, dbbf])
filtered_routes = fp.filter(routes)

# len(filtered_routes) <= len(routes)
```
