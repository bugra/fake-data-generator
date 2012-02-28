'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import random

class randGauss_gen(IModelBehavior):
    arity = (0, 0)
    isNoise = False
    MEAN = 0.5
    STDDEV = 0.3
    def calculate(self):
        return random.gauss(self.MEAN, self.STDDEV)
    def generate_name(self):
        return "gaussian_random(mean={0}, stddev={1})".format(self.MEAN, self.STDDEV)