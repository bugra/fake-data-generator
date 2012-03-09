
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the multiplex operator.

"""

from fakeDataGenerator.model import IModelBehavior
from random import randint

class Multiplex(IModelBehavior):
    arity=(1,1)
    isNoise = True
    def calculate(self, value):
        return (randint(-1,1) * 10.0) + value
    def generate_name(self, name):
        return 'multiplex(%s)' % name

