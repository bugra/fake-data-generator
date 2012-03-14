
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the convertToBase operator.

"""

from fakeDataGenerator.model import IModelBehavior
import math
from random import randint
from string import digits

class ConvertToBase(IModelBehavior):
    arity=(1,1)
    isNoise = False
    conversionBase = randint(2,9)
    def calculate(self, value):
        if value == 0.0 or math.isnan(value) or math.isinf(value):
            return value
        isNegative = False
        if value < 0.0:
            isNegative = True
            
        value = abs(int(value * 100000.0))
        if not value or math.isinf(value) or math.isnan(value):
            return 0.0
        ret = ''
        while value:
            value, i = divmod(value, self.conversionBase)
            ret = digits[i] + ret
        return float(ret)/100000.0*[1,-1][isNegative]
    def generate_name(self, name):
        return 'convertToBase(%s,%d)' % (name, self.conversionBase)

