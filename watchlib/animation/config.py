from abc import ABC
from typing import Tuple

class AnimationConfig(ABC):

    def __init__(self, interval, fig_size, resolution) -> None:
        self.interval = interval
        self.fig_size = fig_size
        self.resolution = resolution

    def set_interval(self, interval: int):
        self.interval = interval

    def set_fig_size(self, shape: Tuple[int, int]):
        self.fig_size = shape

    def set_resolution(self, resolution: int):
        self.resolution = resolution

class WorkoutAnimationConfig(AnimationConfig):

    def __init__(self, interval:int=25, fig_size:Tuple[int,int]=(10,10), resolution:float=0.08, color_on="elevation", rotate=True) -> None:
        super().__init__(interval, fig_size, resolution)
        self.color_on = color_on
        self.rotate = rotate

    def set_color_on(self, color_on: str):
        self.color_on = color_on

    def set_rotate(self, rotate: bool):
        self.rotate = rotate

class ECGAnimationConfig(AnimationConfig):

    def __init__(self, interval:int=None, fig_size:Tuple[int,int]=(20,5), resolution:float=6, length:float=1, speed:float=1, sample:float=512) -> None:
        self.speed = speed
        self.sample = sample
        self.length = length
        super().__init__(interval, fig_size, resolution)
        if self.interval is None: self.__calculate_interval()

    def __calculate_interval(self):
        self.interval = 1000/(self.sample/self.resolution)/self.speed