'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior

class recip_1noise(IModelBehavior):
    arity=(1, 1)
    isNoise = True
    def calculate(self, value):
        if value == 0:
            return 0 #to do something other than fail
        return 1/value
    def generate_name(self, name):
        return '1/'+name

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    