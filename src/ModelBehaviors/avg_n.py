'''
Created on Feb 24, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
from operator import add
from __future__ import division

EXPRESSIVE_NAME = True

class avg_n(IModelBehavior):
    '''
    A model behavior that performs an averaging.
    '''
    arity=(2, None)
    isNoise = False
    def calculate(self, *args):
        total = reduce(add, args)
        return total / len(args) #true division enabled
    
    if EXPRESSIVE_NAME:
        def generate_name(self, *args):
            sumStr = "+".join(args)
            return "({0})/{1}".format(sumStr, len(args))
    else:
        def generate_name(self, *args):
            return "mean({0})".format(", ".join(args))