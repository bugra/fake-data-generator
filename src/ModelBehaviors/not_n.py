
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the NOT operator.

"""

from fakeDataGenerator.model import IModelBehavior

class NotValues(IModelBehavior):
    arity=(2,None)
    isNoise = False
    def calculate(self, *values):
        negative = values[0] < 0.0
        ret = abs(values[0])
        for s in values[1:]:
            if s < 0.0:
                negative = False
            ret -= abs(s)
        return ret * [1.0,-1.0][negative]
    def generate_name(self, *names):
        return 'NOT({0})'.format(", ".join(names))

