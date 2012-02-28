'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import random

class randUnif_gen(IModelBehavior):
    arity=(0,0)
    isNoise = False
    def calculate(self):
        return random.random()
    def generate_name(self):
        return "rand()"