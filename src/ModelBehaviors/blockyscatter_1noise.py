
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the blocky-scatter behavior.

"""

from fakeDataGenerator.model import IModelBehavior
from random import randint

class BlockyScatter(IModelBehavior):
    arity=(1,1)
    isNoise = True
    def __init__(self):
        self.unit = randint(1, 20)
    def calculate(self, value):
        return (randint(-1,1) * self.unit) + value
    def generate_name(self, name):
        return '%s +/-/0 %d' % (name, self.unit)

