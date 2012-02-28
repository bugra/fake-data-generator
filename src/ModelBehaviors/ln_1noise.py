'''
Created on Feb 27, 2012

@author: anorberg
'''

import math
from fakeDataGenerator.model import IModelBehavior

class ln_1noise(IModelBehavior):
    arity=(1, 1)
    isNoise = True
    def calculate(self, value):
        return math.log(value)
    def generate_name(self, name):
        return "ln " + name

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    