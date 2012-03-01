'''
Created on Feb 28, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior

class discretize_1noise(IModelBehavior):
    """IModelBehavior that converts one value to either a 1 or a 0 based on a fixed cutoff."""
    arity=(1,1)
    isNoise = True
    THRESHOLD = 0.5
    def calculate(self, value):
        if value > self.THRESHOLD:
            return 1
        return 0
    def generate_name(self, name):
        return "[{0} -> 0|1 @{1}]".format(name, self.THRESHOLD)