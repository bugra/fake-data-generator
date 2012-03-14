'''
Created on Mar 13, 2012

@author: trobinso

Plugin IModelBehavior that implements randomized propagation of missing values.

'''

from fakeDataGenerator.model import IModelBehavior
import random

class sieve(IModelBehavior):
    arity=(1, 0)
    isNoise = True
    DROP_PROBABILITY = 1/(random.randint(1,25)*10.0)
    def calculate(self,name):
        return [name,float('nan')][random.random() < self.DROP_PROBABILITY]
    def generate_name(self,name):
        return "sieveValues({0}, drop_prob={1})"\
            .format(name, self.DROP_PROBABILITY)