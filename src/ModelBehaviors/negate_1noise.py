'''
Created on Feb 24, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior
class negate_1noise(IModelBehavior):
    arity = (1, 1)
    isNoise = True
    def calculate(self, value):
        """Negates its argument.
        >>> negate_1noise().calculate(-6)
        6
        >>> negate_1noise().calculate(0.25)
        -0.25
        """
        return -value
    def generate_name(self, vname):
        """Prefixes its argument with a - to print a friendly description of this function.
        >>> negate_1noise().generate_name("(A)")
        '-(A)'
        >>> negate_1noise().generate_name("(B+C+D)")
        '-(B+C+D)'
        """
        return "-" + vname
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    