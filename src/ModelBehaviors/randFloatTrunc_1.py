
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the randFloatTrunc operator.

"""

from fakeDataGenerator.model import IModelBehavior
from random import randint

class RandFloatTrunc(IModelBehavior):
    arity=(1,1)
    isNoise = False
    def calculate(self, value):
        return float("{0:.%df}" % randint(0,6)).format(value)
    def generate_name(self, name):
        return 'randFloatTrunc(%s)' % name

