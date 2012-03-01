'''
Created on Feb 27, 2012

@author: anorberg
'''


from fakeDataGenerator.model import IModelBehavior

class absDiff_2(IModelBehavior):
    arity=(2, 2)
    isNoise = False
    def calculate(self, a, b):
        return abs(a-b)
    def generate_name(self, aName, bName):
        return " |{0}-{1}| ".format(aName, bName)

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
    