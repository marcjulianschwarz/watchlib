> class watchlib.animation.WorkoutAnimation(data, config)

You can use `WorkoutAnimation` to create 3D animated plots of your [[WorkoutRoute]]. See [[WorkoutAnimationConfig]] for more details on customizing the animation.

## Parameters
- **data** : [[WorkoutRoute]]
- **config** : [[WorkoutAnimationConfig]]

## Methods
### Animating a route
You can animate a [[WorkoutRoute]] using the `animate()` method. 

**Returns**:
- `matplotlib.animation.FuncAnimation`

**Usage**:

```python
from watchlib.data_handler import DataLoader
from watchlib.animation import WorkoutAnimation

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()

wa = WorkoutAnimation(route=routes[0])
animation = wa.animate()
animation.save("route_animation.mp4")
```

---

### Setting config
You can set a new configuration using the `set_config()` method.
**Parameters**:
- `config` : [[WorkoutAnimationConfig]]

**Usage**:

```python
from watchlib.animation import WorkoutAnimation, WorkoutAnimationConfig

config = WorkoutAnimationConfig(
	fig_size=(10,10),
	color_on="elevation"
)
wa = WorkoutAnimation(route=route, config=config)
```

Of course you can always change the [[WorkoutAnimationConfig]] like this:
```python
wa = WorkoutAnimation(route=route)
wa.config.fig_size = (10,10)
wa.config.color_on = "elevation"
```
