'''
Created on Feb 27, 2012

@author: anorberg
'''

from fakeDataGenerator.model import IModelBehavior

class oneminus_1noise(IModelBehavior):
    arity = (1, 1)
    isNoise = True
    def calculate(self, arg):
        return 1.0-arg
    def generate_name(self, name):
        return "1-"+name

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    