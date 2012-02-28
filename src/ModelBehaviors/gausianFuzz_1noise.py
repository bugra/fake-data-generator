'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import random

class gaussianFuzz_1noise(IModelBehavior):
    arity = (1, 1)
    isNoise = True
    STDDEV = 0.5
    def calculate(self, value):
        return value + random.gauss(0, self.STDDEV)
    def generate_name(self, parentName):
        return "gaussian_random(stddev={0})+".format(self.STDDEV) + parentName