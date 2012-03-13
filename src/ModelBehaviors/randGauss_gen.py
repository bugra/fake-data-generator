'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import random

class randGauss_gen(IModelBehavior):
    arity = (0, 0)
    isNoise = False
    STDDEV_MEAN = 0.5
    MEAN_MEAN = 0
    MEAN_STDDEV = 0.2
    STDDEV_STDDEV = 0.4
    
    def __init__(self):
        self.mean = random.gauss(self.MEAN_MEAN, self.STDDEV_MEAN)
        self.stddev = abs(random.gauss(self.MEAN_STDDEV, self.STDDEV_STDDEV))
    def calculate(self):
        return random.gauss(self.mean, self.stddev)
    def generate_name(self):
        return "gaussian_random(mean={0}, stddev={1})".format(self.mean, self.stddev)