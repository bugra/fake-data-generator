'''
Created on Dec 21, 2011

@author: anorberg
'''
from __future__ import division

import random
import yapsy
from yapsy.IPlugin import IPlugin

NAME_RECURSION_DEPTH = 3 #todo: replace references to this with a config lookup

def identity(x):
    return x

class Node:
    """
    Object that represents a node in the graph model.
    """
    def __init__(self, inputs, name, applyFxn, noiseFxn = identity):
        """
        Constructs a Node object from information about where it fits in the graph.
        Only works for acyclic graphs built in forward order.
        
        Paramters:
            inputs - Iterable containing Node objects that feed into this one.
                     They will be updated to point to this object by this initializer.
                     None becomes the empty list.
            name - String to label this Node.
            applyFxn - IModelBehavior this node is to perform. Can be updated
                       later via the variable name "fxn".
            noiseFxn (optional) - 1-ary IModelBehavior to add noise that shows
                                  up only in column output, not fed to other nodes.
        """
        self.name = name
        if inputs:
            self._inputs = [foo._addOut(self) for foo in inputs]
        else:
            self._inputs = []
        self.fxn = applyFxn
        self.noiseFxn = noiseFxn
        self._outputs = []
        self._resultConsistencyCache = {}
        
    def _addOut(self, newOutNode):
        """
        Private method: add new nodes that receive data from this one.
        Used for traversing the graph later.
        """
        self._outputs.append(newOutNode)
        return self
        
    def addEdge(self, destination):
        destination._inputs.append(self)
        self._outputs.append(destination)
        return self
        
    def removeEdge(self, unDestination):
        try:
            self._outputs.remove(unDestination)
        except ValueError:
            return False
        unDestination._inputs.remove(self)
        return True
        
        
    def calculate(self, cacheKey):
        """
        Calculate the value for the given row of the table. Pulls from cache if
        it's seen this row ID before (any hashable object), and recalculates if
        not. This forced cacheing behavior is strictly required due to the possibility
        of random or partially random calculation functions (especially 0-ary functions).
        """
        if cacheKey not in self._resultConsistencyCache:
            results = []
            for node in self._inputs:
                results.append(node.calculate)
            self._resultConsistencyCache[cacheKey] = self.fxn.calculate(*results)
        return self._resultConsistencyCache[cacheKey]
    
    def columnValue(self, cacheKey):
        """
        Calculate the value for the given row of the table as from calculate,
        then modify the value before returning it to add noise based on the noise function,
        if any was provided. Noise is not cached, so this may vary with multiple invocations.
        """
        return self.noiseFxn.calculate(self.calculate(cacheKey))
    
    def genName(self, remainingRecursion):
        """Generates a friendly name based on what the operation is.
        remainingRecursion is how deeply it should nest names; beyond that, symbolic IDs are used."""
        if remainingRecursion <= 0:
            return self.name
        if not self._inputs:
            #special case: source
            if remainingRecursion == NAME_RECURSION_DEPTH:
                return self.fxn.generate_name()
            else:
                return self.name
        rNext = remainingRecursion - 1
        supernames = ["({0})".format(foo.genName(rNext)) for foo in self._inputs]
        return self.fxn.generate_name(*supernames)
    
    def toGraphViz(self):
        """
        Returns a String that can be used as part of a GraphViz data file.
        Represents all the in-connections to the node. Labels node with generated names.
        """
        statements = ['"{0}:{1}"'.format(self.name, self.genName(NAME_RECURSION_DEPTH))]
        for nodeFrom in self._inputs:
            statements.append(nodeFrom.name + "->" + self.name)
        statements.append("")
        return "; ".join(statements)
    
    def __str__(self):
        """
        Returns a string representation of self.
        """
        return "Node: " + self.name + "- from " + \
            ",".join((foo.name for foo in self._inputs)) + \
            "; into " + ",".join((foo.name for foo in self._outputs))
    
    def _updateReachableSingle(self):
        self.reachableSet = set(self._outputs)
        for dest in self._outputs:
            self.reachableSet.update(dest.reachableSet)
    
    def updateReachable(self):
        steps = 1
        self._updateReachableSingle()
        frontier = set(self._inputs)
        while frontier:
            nextSet = set()
            for element in frontier:
                element._updateReachableSingle()
                steps += 1
                nextSet.update(element._inputs)
            frontier = nextSet
        return steps
        
        

def graphvizEntireThing(headNodes):
    unprocessedNodes = set()
    reachedNodes = set()
    unprocessedNodes.update(headNodes)
    reachedNodes.update(headNodes)
    statements=["digraph Model{"]
    
    while unprocessedNodes:
        nextNode = unprocessedNodes.pop()
        statements.append(nextNode.toGraphViz())
        for supernext in nextNode._outputs:
            if not supernext in reachedNodes:
                reachedNodes.add(supernext)
                unprocessedNodes.add(supernext)

    statements.append("}")
    
    return " ".join(statements)





class IModelBehavior(IPlugin):
    #TODO: DOCUMENT!!!!!!
    @property
    def arity(self):
        """Must be a field-like that contains a 2-element sequence.
        [0] is minimum number of parameters to calculate.
        [1] is maximum number of parameters to calculate, or None for unlimited.
        """
        raise NotImplemented("ModelBehaviorPlugin is abstract and all its plugin hooks must be overridden.")
    
    @property
    def is_noise(self):
        """Must be a field-like that can be used as a boolean:
        True (or evaluates as true)- function is a 1-ary function suitable for use as a scramble function.
        False (or evaluates as false)- anything else.
        """
        raise NotImplemented("ModelBehaviorPlugin is abstract and all its plugin hooks must be overridden.")
    
    def calculate(self, *args):
        """The operation that this function should implement.
        Must take some number of unnamed args- specifically, any number in the range specified by arity.
        This will be dereferenced directly once per node, and then blindly used later.
        Thus, strange getattr tricks to actually secretly call a closure that gives
        random variations on the function are encouraged if appropriate.
        """
        raise NotImplemented("ModelBehaviorPlugin is abstract and all its plugin hooks must be overridden.")
    def generate_name(self, *args):
        """Generate a descriptive name based on the names of the parameters.
        Must take some number of unnamed args- specifically, any number in the range specified by arity.
        The parameters are the generated or symbolic names of previous nodes, parenthesized;
        generate a descriptive name for this node, using those names to describe the operation.
        Used to generate descriptive column names."""
        raise NotImplemented("ModelBehaviorPlugin is abstract and all its plugin hooks must be overridden.")
    @classmethod
    def implementations(cls, paths):
        """Return an iterable of plugin-info for every locatable implementation of this interface.
        """
        manager = yapsy.PluginManager()
        manager.setPluginPlaces(paths)
        manager.setCategoriesFilter({
            "ModelBehavior" : IModelBehavior,                         
            })
        manager.collectPlugins()
        return manager.getPluginsOfCategory("ModelBehavior")
    
def extendFunctionLookup(listlist, nonElimFxns, newMax):
    #TODO: fix to work with indefs (None as a limit)
    if len(listlist) > newMax:
        dupe = [fxn for fxn in nonElimFxns]
        return dupe
    newLen = newMax + 1
    low = len(listlist)
    while len(listlist) < newLen:
        listlist.append([])
    remainingFxns = []
    for fxn in nonElimFxns:
        if fxn.arity[1] < low:
            pass
        if fxn.arity[1] > newMax:
            remainingFxns.append(fxn)
        for x in range(max(low, fxn.arity[0]), min(newLen, fxn.arity[1] + 1)):
            listlist[x].append(fxn)
    return remainingFxns
    
class IdentityBehavior(IModelBehavior):
    arity = (1, 1)
    is_noise = True
    def calculate(self, oneArg):
        return oneArg    
    def generate_name(self, oneName):
        return oneName
    
def randomElement(ls):
    dex = random.randint(len(ls))
    return ls[dex]     

DEFAULT_ARITY_MAX = 4
    
def workingModelFromPygraph(graph, fxns, bonus_identity = 0):
    """Takes a pygraph.digraph.digraph object, an iterable of
    IModelBehavior that lists all potential calculation functions,
    and the number of "bonus instances" of the identity function
    that should be thrown into the fuzzer pool."""
    # generate collection of functions at each arity up to 4. extend later as needed
    noise = [fxn for fxn in fxns if fxn.is_noise]
    for x in range(0, bonus_identity):
        noise.append(IdentityBehavior())
        
    arityTable = []
    fxns = extendFunctionLookup(arityTable, fxns, DEFAULT_ARITY_MAX)
    #dependency-order traversal
    cleared = set()
    zeroAry = [node for node in graph.nodes() if not graph.incidents(node)]
    frontier = set(zeroAry)
    labelsToModelNodes = {}
    
    def drawAppropriateFxn(forThisLabel):
        arity = len(graph.incidents(forThisLabel))
        #NEXT UP: check arityTable length, grab random, raise if too short
        if len(arityTable) < arity:
            fxns = extendFunctionLookup(arityTable, fxns, arity)
        
        valids = arityTable[arity]
        
        if not valids:
            raise ValueError("There exists a node for which no function exists- no {0}-ary functions: {1}".format(arity, forThisLabel))
        
        return randomElement(valids)
    
    while frontier:
        nextNode = frontier.pop()
        cleared.add(nextNode)
        foo = Node((labelsToModelNodes[incoming] for incoming in graph.incidents(nextNode)),
                   nextNode,
                   drawAppropriateFxn(nextNode),
                   randomElement(noise))
        labelsToModelNodes[nextNode] = foo
        for child in graph.neighbors(nextNode):
            if(cleared.issuperset(graph.incidents(child))):
                frontier.add(child)
    
    return labelsToModelNodes.values(), zeroAry
