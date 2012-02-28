'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior

class cmp_2(IModelBehavior):
    arity = (2, 2)
    isNoise = False
    def calculate(self, a, b):
        if(a > b): return 0
        if(b > a): return 1
        return 0.5
    def generate_name(self, a, b):
        return "(({0} cmp {1}) + 1)/2".format(a, b)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    