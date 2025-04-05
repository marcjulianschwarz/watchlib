
> class watchlib.animation.WorkoutAnimationConfig(data, config)

You can use `WorkoutAnimationConfig` to customize/configure  a [[WorkoutAnimation]].


```python
from watchlib.data_handler import DataLoader
from watchlib.animation import WorkoutAnimation, WorkoutAnimationConfig

dl = DataLoader("path/to/apple_health_export")
routes = dl.load_routes()

config = WorkoutAnimationConfig(
	fig_size=(8,8),
	color_on="speed",
	resolution=0.5
)

wa = WorkoutAnimation(route=routes[0], config=config)
animation = wa.animate()
animation.save("route_animation.mp4")
```


## Parameters
- **interval** : int = 25
- **fig_size** : Tuple[int, int] = (10,10)
- **resolution** : float = 0.08
- **color_on** : str = "elevation"
- **rotate**: bool = True

### color_on
The `color_on` parameter can take following values:
- "speed"
- "elevation"
- "vAcc" -> vertical acceleration
- "hAcc" -> horizontal acceleration
- "course"

You can access these constants like this:
```python
from watchlib.animation import WORKOUT_OPTIONS

WORKOUT_OPTIONS["color_on"]
# Returns:
# ["speed", "elevation", "vAcc", "hAcc", "course"]
```

