
"""
Created on Feb 27, 2012

@author: trobinso

Plugin IModelBehavior that implements something similar to conflicting upregulation/downregulation factors.

"""

from fakeDataGenerator.model import IModelBehavior

class Downregulate(IModelBehavior):
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
        return '{0} downregulated by: {1}'.format(names[0], ", ".join(names[1:]))

