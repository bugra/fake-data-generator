'''
Created on Feb 27, 2012

@author: anorberg
'''
from __future__ import division
from fakeDataGenerator.model import IModelBehavior

class smallRatio_2(IModelBehavior):
    arity=(2, 2)
    isNoise = False
    def calculate(self, a, b):
        a, b = abs(a), abs(b)
        if a > b:
            a, b = b, a
        return a / b
    def generate_name(self, a, b):
        return "|{0}:{1} ratio|".format(a, b)