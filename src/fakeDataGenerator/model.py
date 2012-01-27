'''
Created on Dec 21, 2011

@author: anorberg
'''
from __future__ import division

import random
import sys

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

def shuffle(shuffleMe):
    for x in range(0, len(shuffleMe)):
        grab = random.randrange(x, len(shuffleMe))
        temp = shuffleMe[x]
        shuffleMe[x] = shuffleMe[grab]
        shuffleMe[grab] = temp

def lateShuffleRandomGraph(sources, graphSize, arityList):
    x = 0;
    deck = []
    sourceNodes = []
    while x < sources:
        foo = Node([], str(x), identity)
        deck.append(foo)
        sourceNodes.append(foo)
        x += 1
    discardPile = []
    shuffle(deck)
    while x < graphSize:
        arityRand = random.random()
        arity = 0
        while arityRand > arityList[arity]:
            arity += 1
        arity += 1
        thingie = []
        for q in range(0, arity):
            if not deck:
                deck = discardPile
                shuffle(deck)
                discardPile = []
            foo = deck.pop()
            thingie.append(foo)
            discardPile.append(foo)
        node = Node(thingie, str(x), identity)
        deck.append(node)
        shuffle(deck)   
        x += 1
    return sourceNodes

ROOT_SENTINEL = Node([], "ROOT-SENTINEL!NOT-A-NODE", identity)

class SearchState:
    """
    Represents the state of searching through parents of one node.
    Used only for parentdistance.
    """
    def __init__(self, singleNode, bit, goal):
        self.zone = set()
        self.zone.add(singleNode)
        self.frontier = set()
        self.frontier.add(singleNode)
        self.mask = 1 << bit
        self.goal = 2 ** goal - 1
    
    def generationZero(self, nodeTable):
        for oneNode in self.frontier:
            if oneNode not in nodeTable:
                nodeTable[oneNode] = self.mask;
            else:
                nodeTable[oneNode] |= self.mask;
            if nodeTable[oneNode] & self.goal == self.goal:
                return True
        return False
        
    def relaxAndCheck(self, nodeTable):
        neoFrontier = set()
        win = False
        for node in self.frontier:
            runMe = node._inputs
            if not node._inputs:
                #ha, ha, you have no parents orphan boy
                runMe = [ROOT_SENTINEL]
            for upwards in runMe:
                if upwards not in self.zone:
                    self.zone.add(upwards)
                    neoFrontier.add(upwards)
                    if upwards not in nodeTable:
                        nodeTable[upwards] = 0
                    nodeTable[upwards] |= self.mask
                    if nodeTable[upwards] & self.goal == self.goal:
                        win = True
        self.frontier = neoFrontier
        return win;

def parentdistance(nodes):
    searchers = []
    scoreboard = {}
    for x in enumerate(nodes):
        searchers.append(SearchState(x[1], x[0], len(nodes)))
    
    for state in searchers:
        if state.generationZero(scoreboard):
            return 0
    generation = 1
    while True:
        for state in searchers:
            if state.relaxAndCheck(scoreboard):
                return generation
        generation += 1

def overutilization_factory(rate):
    def overutilization(node, ignored):
        return 1.0 / (rate ** len(node._outputs))
    return overutilization

def parentdistance_reformulated(node, moreNodes):
    inputThing = [node]
    inputThing.extend(moreNodes)
    return 1.0 / (2 ** parentdistance(inputThing))    

kickout_overutil = overutilization_factory(4)
def kickoutCombo(node, moreNodes):
    return kickout_overutil(node, moreNodes) * parentdistance_reformulated(node, moreNodes)

def decliningUsageRateGraph(sources, graphSize, rawArityList):
    return rejectableGraph(sources, graphSize, rawArityList, overutilization_factory(2))

def limitedSplayGraph(sources, graphSize, rawArityList):
    return rejectableGraph(sources, graphSize, rawArityList, kickoutCombo)

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

def rejectableGraph(sources, graphSize, rawArityList, acceptFxn):
    bucket = []
    sourceNodes = []
    arityList = [0.0]
    arityList.extend(rawArityList)
    for x in range(0, sources):
        raw = Node([], str(x), identity)
        sourceNodes.append(raw)
    bucket.extend(sourceNodes)
    for x in range(len(sourceNodes), graphSize):
        nodeInputs = []
        arityRand = random.random()
        arity = 0
        while arityRand > arityList[arity]:
            arity += 1
            candidate = bucket[random.randrange(0, len(bucket))]
            while candidate in nodeInputs or acceptFxn(candidate, nodeInputs) < random.random():
                candidate = bucket[random.randrange(0, len(bucket))]
            nodeInputs.append(candidate)
        raw = Node(nodeInputs, str(x), identity)
        bucket.append(raw)
    return sourceNodes

ARITY_LIST = [0.25, 0.5, 0.75, 1.0]

if __name__ == "__main__":
    #print graphvizEntireThing(limitedSplayGraph(int(sys.argv[2]), int(sys.argv[1]), ARITY_LIST))
    sourceNum = int(sys.argv[2])
    graphSize = int(sys.argv[1])
    print graphvizEntireThing(IdeCozmanShuffle(sourceNum, sourceNum * 2, len(ARITY_LIST), graphSize))
        