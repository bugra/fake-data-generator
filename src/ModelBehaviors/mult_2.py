'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior

class mult_2(IModelBehavior):
    arity=(2, 2)
    isNoise = False
    def calculate(self, a, b):
        return a * b
    def generate_name(self, a, b):
        return "{0} * {1}".format(a, b)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    