import numpy as np

class Stat:

    def __init__(self, data: dict):
        self.data = data


    # steps
    def steps(self):
        return np.array(self.data["HKQuantityTypeIdentifierStepCount"]).astype("int64")

    def steps_sum(self):
        return sum(self.steps())

    def steps_average(self):
        return np.mean(self.steps())
    

    # body weight
    def weight(self):
        return np.array(self.data["HKQuantityTypeIdentifierBodyMass"]).astype("float")


    # body height
    def height(self):
        return np.array(self.data["HKQuantityTypeIdentifierHeight"]).astype("float")
