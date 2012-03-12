'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import random

class gaussianFuzz_1noise(IModelBehavior):
    arity = (1, 1)
    isNoise = True
    STDDEV_STDDEV = 0.75
    MEAN_STDDEV = 0.25
    STDDEV_MEAN = 1
    
    def __init__(self):
        self.mean = random.gauss(0, self.STDDEV_MEAN)
        self.stddev = abs(random.gauss(self.MEAN_STDDEV, self.STDDEV_STDDEV))
    
    def calculate(self, value):
        return value + random.gauss(self.mean, self.stddev)
    def generate_name(self, parentName):
        return "gaussian_random(mean={0}, stddev={1})+".format(self.mean, self.stddev) + parentName