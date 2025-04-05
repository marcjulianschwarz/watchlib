> class watchlib.filtering.DiagonalBBoxFilter()

This filter will only select routes that have a longer diagonal from the point in the most southwest to the point in the most northeast position on the route than `diagonal_distance`. It uses the [Haversine Formula](https://en.wikipedia.org/wiki/Haversine_formul) to calculate the distance between two points on earths surface.

```python
from watchlib.filtering import BBoxFilter
```


## Parameters
- **diagonal_distance** : `float` (in kilometers)
## Methods
### Filtering
Use the `filter()` method to filter a list of [[WorkoutRoute]] according to `diagonal_distance`.

**Parameters**:
- `routes` : `List[WorkoutRoute]` -> [[WorkoutRoute]]

**Returns**: 
- `List[WorkoutRoute]` → [[WorkoutRoute]]

**Usage**:
`routes` is a list of [[WorkoutRoute]] previously loaded using [[DataLoader]] or [[CacheHandler]].

```python
from watchlib.filtering import DiagonalBBoxFilter

dbb_filter = DiagonalBBoxFilter(diagonal_distance=10)
filtered_routes = dbb_filter.filter(routes)

# len(filtered_routes) <= len(routes)
```

---

## Utility Methods

### Get maximum diagonal distance
Use the `max_bbox()` method to get the maximum diagonal distance from a list of [[WorkoutRoute]].

**Parameters**:
- `routes` : `List[WorkoutRoute]`

**Returns**:
- `float`

**Usage**:
`routes` is a list of [[WorkoutRoute]] previously loaded using [[DataLoader]] or [[CacheHandler]].

```python
from watchlib.filtering import DiagonalBBoxFilter

max_diagonal_distance = DiagonalBBoxFilter.max_bbox(routes)
```

---

### Get minimum diagonal distance

Use the `min_bbox()` method to get the minimum diagonal distance from a list of [[WorkoutRoute]].

**Parameters**:
- `routes` : `List[WorkoutRoute]`

**Returns**:
- `float`

**Usage**:
`routes` is a list of [[WorkoutRoute]] previously loaded using [[DataLoader]] or [[CacheHandler]].

```python
from watchlib.filtering import DiagonalBBoxFilter

min_diagonal_distance = DiagonalBBoxFilter.min_bbox(routes)
```