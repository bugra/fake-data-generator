'''
Created on Feb 24, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import operator

class add_n(IModelBehavior):
    '''
    IModelBehavior for an n-ary function that adds values together.
    '''
    arity=(2, None)
    isNoise = False
    def calculate(self, *args):
        return reduce(operator.add, args)
    def generate_name(self, *args):
        return "+".join(args)