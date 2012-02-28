'''
Created on Feb 27, 2012

@author: anorberg
'''
from __future__ import division

from fakeDataGenerator.model import IModelBehavior
import random

class randZeroOne_gen(IModelBehavior):
    arity = (0, 0)
    isNoise = False
    RATE = 0.5
    def calculate(self):
        if random.random() < self.RATE:
            return 1
        return 0
    def generate_name(self):
        return "<{0:.1%} coin flip>".format(self.RATE)
    
if __name__ == '__main__':
    z = 0
    TRIALS = 1000000
    generator = randZeroOne_gen()
    for x in range(TRIALS):
        if generator.calculate():
            z += 1
    print "{0:.5%} observed".format(z/TRIALS)
    print generator.generate_name()