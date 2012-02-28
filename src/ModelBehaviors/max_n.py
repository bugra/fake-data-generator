'''
Created on Feb 27, 2012

@author: anorberg

Plugin IModelBehavior that implements the "max" operation.
'''

from fakeDataGenerator.model import IModelBehavior

class max_n(IModelBehavior):
    arity=(2, None)
    isNoise = False
    def calculate(self, *values):
        return max(values)
    def generate_name(self, *names):
        return 'max({0})'.format(", ".join(names))