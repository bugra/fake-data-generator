'''
Created on Dec 21, 2011

@author: anorberg
'''
from __future__ import division

import random
import sys
import yapsy

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
            applyFxn - Operation this node is to perform. Can be updated
                       later via the variable name "fxn".
            noiseFxn (optional) - 1-ary function to add noise that shows
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
            self._resultConsistencyCache[cacheKey] = self.fxn(*results)
        return self._resultConsistencyCache[cacheKey]
    
    def columnValue(self, cacheKey):
        """
        Calculate the value for the given row of the table as from calculate,
        then modify the value before returning it to add noise based on the noise function,
        if any was provided. Noise is not cached, so this may vary with multiple invocations.
        """
        return self.noiseFxn(self.calculate(cacheKey))
    
    def toGraphViz(self):
        """
        Returns a String that can be used as part of a GraphViz data file.
        Represents all the in-connections to the node.
        """
        statements = [self.name]
        for nodeFrom in self._inputs:
            statements.append(nodeFrom.name + "->" + self.name)
        statements.append("")
        return "; ".join(statements);
    
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



def IdeCozmanShuffle(sourceLow, sourceHigh, inMax, graphSize, iterations=None):
    '''An implementation of Jaime S. Ide and Fabio G. Cozman's Markov
    algorithm for uniform generation of Bayesian networks,
    modified to restrict the space to the constraints we need.'''
    if iterations is None:
        iterations = graphSize * graphSize
    
    nodes = []
    roots = []
    
    #build list-shaped graph with random sources linked in
    
    for q in range(graphSize - sourceLow + 1):
        reachableSet = set(nodes)
        nodes.append(Node(None, str(q), identity))
        if len(nodes) > 1:
            nodes[-1].addEdge(nodes[-2])
        nodes[-1].reachableSet = reachableSet
    
    roots.append(nodes[-1])
    
    while len(roots) < sourceLow:
        roots.append(Node(None, str(len(nodes)), identity))
        foo = nodes[random.randint(0, len(roots) - 1)]
        while not foo._inputs:    
            foo = nodes[random.randint(0, len(roots) - 1)]
        roots[-1].addEdge(foo)
        nodes.append(roots[-1])
        roots[-1].updateReachable()
        
    
    #N times:
    for q in range(iterations):
        #try removing something
        source = nodes[random.randint(0, len(nodes) - 1)]
        dest = source
        while dest == source:
            dest = nodes[random.randint(0, len(nodes) - 1)]

        if len(dest._inputs) != 1 or len(roots) < sourceHigh:
                #prevents tryCut call if this would go over the source limit 
            if tryCut(source, dest) and not dest._inputs:
                roots.append(dest)

        #try adding something
        source = nodes[random.randint(0, len(nodes) - 1)]
        dest = source
        while dest == source:
            dest = nodes[random.randint(0, len(nodes) - 1)]
            
        if (dest._inputs or len(roots) > sourceLow) and len(dest._inputs) < inMax:
            if tryAdd(source, dest) and len(dest._inputs) == 1:
                roots.remove(dest) #slow... consider alternate data structure
        
    return roots

def isConnected(source, dest, skipLinks = set()):
    done = set()
    frontier = set([source])
    while frontier:
        thing = frontier.pop()
        done.add(thing)
        for path in thing._outputs:
            if (thing, path) in skipLinks:
                continue
            if path == dest:
                return True
            if path in done:
                continue
            frontier.add(path)
        for path in thing._inputs:
            if (path, thing) in skipLinks:
                continue
            if path == dest:
                return True
            if path in done:
                continue
            frontier.add(path)
    return False

def tryCut(source, dest):
    if not isConnected(source, dest, set([(source, dest)])):
        return False
    if source.removeEdge(dest):
        source.updateReachable()
        return True
    return False
    
def tryAdd(source, dest):
    if source in dest.reachableSet:
        return False
    if dest in source._outputs:
        return False
    if source.addEdge(dest):
        source.updateReachable()
    return True

class IModelBehavior(yapsy.IPlugin):
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
    
def randomElement(ls):
    dex = random.randint(len(ls))
    return ls[dex]     

DEFAULT_ARITY_MAX = 4
    
def workingModelFromPygraph(graph, fxns, bonus_identity = 0):
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

ARITY_LIST = [0.25, 0.5, 0.75, 1.0]

if __name__ == "__main__":
    #print graphvizEntireThing(limitedSplayGraph(int(sys.argv[2]), int(sys.argv[1]), ARITY_LIST))
    sourceNum = int(sys.argv[2])
    graphSize = int(sys.argv[1])
    print graphvizEntireThing(IdeCozmanShuffle(sourceNum, sourceNum * 2, len(ARITY_LIST), graphSize))
        