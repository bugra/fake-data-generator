'''
Created on Feb 27, 2012

@author: anorberg

Plugin IModelBehavior that implements the "min" operation.
'''

from fakeDataGenerator.model import IModelBehavior

class min_n(IModelBehavior):
    arity=(2, None)
    isNoise = False
    def calculate(self, *values):
        return min(values)
    def generate_name(self, *names):
        return 'min({0})'.format(", ".join(names))