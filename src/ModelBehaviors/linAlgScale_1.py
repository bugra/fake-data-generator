
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the scale operator.

"""

from fakeDataGenerator.model import IModelBehavior
from random import random

class Scale(IModelBehavior):
    arity=(1,1)
    isNoise = False
    scaleValue = random.random() * 10.0
    def calculate(self, value):
        return self.scaleValue * value
    def generate_name(self, name):
        return '%s + %.6f' % (name, self.scaleValue)

