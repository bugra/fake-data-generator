'''
Created on Feb 24, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
import math

class zeroOne_truncate_1noise(IModelBehavior):
    arity = (1, 1)
    isNoise = True
    def calculate(self, value):
        """Truncate to the range [0, 1).
        
        All integers will wind up 0:
        
        >>> zeroOne_truncate_1noise().calculate(random.randint(0, 100000))
        0.0
        
        Otherwise, a value is truncated to its fractional part:
        
        >>> zeroOne_truncate_1noise().calculate(8.25)
        0.25
        >>> zeroOne_truncate_1noise().calculate(93.5)
        0.5
        
        Values already in [0, 1) are unchanged:
        >>> x = random.random()
        >>> x == zeroOne_truncate_1noise().calculate(x)
        True
        
        Negative values are processed by absolute value:
        >>> zeroOne_truncate_1noise().calculate(-4.125)
        0.125
        >>> zeroOne_truncate_1noise().calculate(-6.75)
        0.75
        
        This will not produce a negative zero.
        """
        if math.isnan(value) or math.isinf(value):
            return value
        value = abs(value)
        value -= float(int(value))
        return value
        
    def generate_name(self, parentName):
        """Describes the operation as 'parentName ~%~ 1.0', as an adaptation of modulus syntax.
        While the modulus operation is defined only over the integers, this is conceptually similar.
        
        >>> zeroOne_truncate_1noise().generate_name("foo")
        'foo ~%~ 1.0'
        """
        return "{0} ~%~ 1.0".format(parentName)
    
    
if __name__ == "__main__":
    import doctest
    import random
    doctest.testmod(verbose=True)