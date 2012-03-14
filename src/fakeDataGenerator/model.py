'''
Created on Dec 21, 2011

@author: anorberg
'''
from __future__ import division

import random
import yapsy
from yapsy.PluginManager import PluginManager
import spiralPointDistribution
import pointsToOutwardDigraph
from yapsy.IPlugin import IPlugin

graphviz_recursion_depth = 1 #todo: replace references to this with a config lookup

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
        """
        Add an edge from this node to a specified node.
        """
        destination._inputs.append(self)
        self._outputs.append(destination)
        return self
        
    def removeEdge(self, unDestination):
        """
        Remove an existing edge to a specified node. Returns False
        if that edge does not already exist, otherwise returns True.
        """
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
                results.append(node.calculate(cacheKey))
            self._resultConsistencyCache[cacheKey] = self.fxn.calculate(*results)
        return self._resultConsistencyCache[cacheKey]
    
    def columnValue(self, cacheKey):
        """
        Calculate the value for the given row of the table as from calculate,
        then modify the value before returning it to add noise based on the noise function,
        if any was provided. Noise is not cached, so this may vary with multiple invocations.
        """
        return self.noiseFxn.calculate(self.calculate(cacheKey))
    
    def genName(self, remainingRecursion, first = True):
        """Generates a friendly name based on what the operation is.
        remainingRecursion is how deeply it should nest names; beyond that, symbolic IDs are used.
        genName calls itself recursively, and outside calls under most circumstances
        should not tinker with the "First" flag, which modifies handling of 0-ary operations.
        (0-ary operations are assumed to be 'generators' and referred to
        symbolically at all levels other than the level defining only the operation.)
        """
        if remainingRecursion <= 0:
            return self.name
        if not self._inputs:
            #special case: source
            if first:
                return self.fxn.generate_name()
            else:
                return self.name
        rNext = remainingRecursion - 1
        supernames = ["({0})".format(foo.genName(rNext, False)) for foo in self._inputs]
        return self.fxn.generate_name(*supernames)
    
    def toGraphViz(self):
        """
        Returns a String that can be used as part of a GraphViz data file.
        Represents all the in-connections to the node. Labels node with generated names.
        """
        statements = ['"{0}" [label = "{0}:{1}"]'.format(self.name, self.genName(graphviz_recursion_depth))]
        for nodeFrom in self._inputs:
            statements.append('"{0}"->"{1}"'.format(nodeFrom.name, self.name))
        statements.append("")
        return "; ".join(statements)
    
    def __str__(self):
        """
        Returns a descriptive string representation of self.
        """
        return "Node: " + self.name + "- from " + \
            ",".join((foo.name for foo in self._inputs)) + \
            "; into " + ",".join((foo.name for foo in self._outputs))
    
    def _updateReachableSingle(self):
        """
        Internal: used as part of the reachableSet calculation.
        """
        self.reachableSet = set(self._outputs)
        for dest in self._outputs:
            self.reachableSet.update(dest.reachableSet)
    
    def updateReachable(self):
        """
        Re-scan for which nodes in the graph can be,
        directly or indirectly, reached by this one. Used
        as part of cycle-detection and break-detection algorithms.
        """
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
    """
    Calculates a GraphViz DOT representation of a graph and returns it as a string.
    Uses the generated names to a recursion depth of graphviz_recursion_depth, which
    can be written into to customize this behavior.
    
    Parameter is the 0-ary nodes of the graph; other nodes are found via search.
    
    Return value is a string containing the GraphViz representation.
    """
    unprocessedNodes = set()
    reachedNodes = set()
    unprocessedNodes.update(headNodes)
    reachedNodes.update(headNodes)
    statements=["digraph{"]
    
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
    """
    Plugin interface for behaviors the model can perform on values at each node in the graph.
    Must be implemented and complemented by an appropriate yapsy-plugin info file for each
    behavior operation. Includes calculation function, metadata, and friendly name generation function.
    """
    @property
    def arity(self):
        """Must be a field-like that contains a 2-element sequence.
        [0] is minimum number of parameters to calculate.
        [1] is maximum number of parameters to calculate, or None for unlimited.
        """
        raise NotImplemented("ModelBehaviorPlugin is abstract and all its plugin hooks must be overridden.")
    
    @property
    def isNoise(self):
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
    
def modelBehaviorImplementations(paths):
    """
    Return an iterable of plugin-info for every locatable implementation of this interface on a given path.
    PyDev for Eclipse reports a compilation error here on a line that is actually legal Python due to
    the schedule upon which module resolution and imports happen.
    """
    manager = PluginManager()
    manager.setPluginPlaces(paths)
    from fakeDataGenerator.model import IModelBehavior as foreignModelBehavior
    #hey PyDev: the previous line is weird, but is actually legal
    manager.setCategoriesFilter({
        "ModelBehavior" : foreignModelBehavior,                         
        })
    manager.collectPlugins()
    return manager.getPluginsOfCategory("ModelBehavior")
    
def _extendFunctionLookup(listlist, nonElimFxns, newMax):
    """
    Internal function used during the construction of a model from a Pygraph.
    Extends a lookup table of arity to candidate functions to include a new
    arity.
    
    Modifies its first argument. Returns a new, shorter list of functions:
    functions that may yet cover arities the list hasn't reached yet.
    Functions with a maximum arity that has already been covered
    will have been removed from this new list.
    The second argument is not modified.
    """
    if len(listlist) > newMax:
        dupe = [fxn for fxn in nonElimFxns]
        return dupe
    newLen = newMax + 1
    low = len(listlist)
    while len(listlist) < newLen:
        listlist.append([])
    remainingFxns = []
    for fxn in nonElimFxns:
        if fxn.arity[1] is not None and fxn.arity[1] < low:
            continue
        if fxn.arity[1] is None or fxn.arity[1] > newMax:
            remainingFxns.append(fxn)
        top = newLen
        if fxn.arity[1] is not None:
            top = min(top, fxn.arity[1] + 1)
        for x in range(max(low, fxn.arity[0]), top):
            listlist[x].append(fxn)
    return remainingFxns
    
class IdentityBehavior(IModelBehavior):
    """
    An implementation of IModelBehavior: the 1ary function that does nothing at all but return its argument.
    """
    arity = (1, 1)
    isNoise = True
    def calculate(self, oneArg):
        """Returns its argument."""
        return oneArg    
    def generate_name(self, oneName):
        """Returns its argument, as the most concise description of the function."""
        return oneName
    
def randomElement(ls):
    """
    Helper function. Draws a random element off a list, selected uniformly.
    """
    dex = random.randint(0, len(ls)-1)
    return ls[dex]     

DEFAULT_ARITY_MAX = 4
    
def workingModelFromPygraph(graph, fxns, bonus_identity = 0):
    """Takes a pygraph.digraph.digraph object, an iterable of
    IModelBehavior that lists all potential calculation functions,
    and the number of "bonus instances" of the identity function
    that should be thrown into the fuzzer pool."""
    # generate collection of functions at each arity up to 4. extend later as needed
    noise = [fxn for fxn in fxns if fxn.isNoise]
    for x in range(0, bonus_identity):
        noise.append(IdentityBehavior())
        
    arityTable = []
    fxns = _extendFunctionLookup(arityTable, fxns, DEFAULT_ARITY_MAX)
    #dependency-order traversal
    cleared = set()
    zeroAry = [node for node in graph.nodes() if not graph.incidents(node)]
    frontier = set(zeroAry)
    labelsToModelNodes = {}
    
    class functionBox(object):
        #box a closure so fxns is writebackable
        def __init__(self, fxns):
            self.fxns = fxns
    
        def drawAppropriateFxn(self, forThisLabel):
            arity = len(graph.incidents(forThisLabel))
            #NEXT UP: check arityTable length, grab random, raise if too short
            if len(arityTable) <= arity:
                self.fxns = _extendFunctionLookup(arityTable, self.fxns, arity)
            valids = arityTable[arity]
            if not valids:
                raise ValueError("There exists a node for which no function exists- no {0}-ary functions: {1}".format(arity, forThisLabel))
            return randomElement(valids)
        
        def __call__(self, forThisLabel):
            return self.drawAppropriateFxn(forThisLabel)
    
    drawAppropriateFxn = functionBox(fxns)
    
    while frontier:
        nextNode = frontier.pop()
        cleared.add(nextNode)
        foo = Node((labelsToModelNodes[incoming] for incoming in graph.incidents(nextNode)),
                   nextNode,
                   drawAppropriateFxn(nextNode).__class__(), #new instance, so init can be useful
                   randomElement(noise).__class__())
        labelsToModelNodes[nextNode] = foo
        for child in graph.neighbors(nextNode):
            if(cleared.issuperset(graph.incidents(child))):
                frontier.add(child)
    
    return labelsToModelNodes.values(), [labelsToModelNodes[nodeName] for nodeName in zeroAry]



def buildRandomModel(nPoints, nSeeds, r0, delta, spread, lumpage, behaviorPaths, pruner, prunerPaths = None, name_prefix="", bonus_identity = 3):
    """
    Builds a running, randomly-generated network model from the given parameters.
    
    Parameters:
        nPoints - Number of nodes that should be in the resulting network, including seed points.
        nSeeds - Number of nodes that are "seeds"- have an in-degree of 0. Must be at least 1.
        r0 - A parameter that defines how strongly the first few nodes shape the graph. Large values will result in more separation between generators.
        delta - A parameter that, in practice, defines how quickly distances grow. Leads to fewer edges as the graph goes further down.
        spread - A parameter that affects how many "clusters" the graph will eventually wind up with.
        lumpage - An integer that affects how aggressively points cluster. 0 will result in a graph of a random scattering of points, but
                  otherwise low values result in stricter clusters.
        behaviorPaths - A list of strings representing file paths that yapsy should search for IModelBehavior plugins.
        pruner - either a pointsToOutwardDigraph.IPruneEdges to use to prune the graph to its final form,
                 or the name of a plugin implementing IPruneEdges that can be loaded for the purpose.
        prunerPaths - Ignored if pruner is not a string. If pruner is a string, that pruner, as the name of a Yapsy plugin,
                      will be searched for in these paths.
        namePrefix - Prefix for all node names (inserted after @ for non-generator nodes). Used when welding multiple graphs.
        bonus_identiy - Number of additional times to add the IdentityBehavior to the pool of IModelBehavior that
                        is drawn from for noise functions. Used to increase the odds that a column will not be
                        intentionally semi-randomized or modified before presentation to the column printer.
                        Use 0 to keep standard equal probabilities.
    """
    points = spiralPointDistribution.spiralPointDistribution(nPoints, nSeeds, r0, delta, spread, lumpage)
    rawCompleteGraph = pointsToOutwardDigraph.graphFromPoints(points, nSeeds)
    rawCompleteGraph = pointsToOutwardDigraph.friendly_rename(rawCompleteGraph, name_prefix)
    if isinstance(pruner, str):
        #TODO: fix
        candidatePruners = pointsToOutwardDigraph.prunerImplementations(prunerPaths)
        for pluginInfo in candidatePruners:
            if pluginInfo.name == pruner:
                pruner = pluginInfo.plugin_object
                pruner.activate()
                break
        raise ValueError("No pruner by name {0} found in specified paths.".format(pruner))
    trimmedGraph = pruner.prune(rawCompleteGraph)
    
    function_plugins =modelBehaviorImplementations(behaviorPaths)
    functions = [plugin.plugin_object for plugin in function_plugins]
    return workingModelFromPygraph(trimmedGraph, functions, bonus_identity)


if __name__ == "__main__":
    """Crude, prototypical approach to fake data table generation."""
    #smoke test
    import candidate_test_pruners
    nodes, head = buildRandomModel(50, 4, 1, 0.5, 0.3, 2, ['U:\\mercurial\\fake-data-generator\\src\\ModelBehaviors'], candidate_test_pruners.bigDelta())
    with open("E:\\debris\\whatever.gv", "w") as gvfile:
        gvfile.write(graphvizEntireThing(head))
        gvfile.flush()
    import csv
    with open("E:\\debris\\fakeData.tsv", "wb") as tsvfile:
        cleanWriter = csv.writer(tsvfile, dialect='excel-tab')
        cleanWriter.writerow(["{0}:{1}".format(node.name, node.genName(4)) for node in nodes])
        for x in range(200):
            key = object()
            cleanWriter.writerow([str(node.calculate(key)) for node in nodes])
            if not x % 100:
                print x, "rows done"
        tsvfile.flush()