
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the translate operator.

"""

from fakeDataGenerator.model import IModelBehavior
from random import random

class Translate(IModelBehavior):
    arity=(1,1)
    isNoise = False
    translationValue = (random.random() * 20.0) - 10.0
    
    def calculate(self, value):
        return self.translationValue + value
    def generate_name(self, name):
        return 'translate(%s,%.6f)' % (name, self.translationValue)

