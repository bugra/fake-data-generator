
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the convertToBase operator.

"""

from fakeDataGenerator.model import IModelBehavior
from random import randint
from string import digits

class ConvertToBase(IModelBehavior):
    arity=(1,1)
    isNoise = False
    conversionBase = randint(2,9)
    def calculate(self, value):
        if value == 0.0:
            return 0.0
        value = int(value * 100000.0)
        ret = ''
        while value:
            value, i = divmod(value, self.conversionBase)
            ret = digits[i] + ret
        return float(ret)/100000.0
    def generate_name(self, name):
        return 'convertToBase(%s,%d)' % (name, self.conversionBase)

