
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements the AND operator.

"""

from fakeDataGenerator.model import IModelBehavior

class AndValues(IModelBehavior):
    arity=(2,None)
    isNoise = False
    def calculate(self, *values):
        ret = int(values[0]*100000.0)
        for s in values[1:]:
            ret &= int(s*100000.0)
        return ret/100000.0
    def generate_name(self, *names):
        return 'AND({0})'.format(", ".join(names))

