'''
Created on Feb 22, 2012

@author: anorberg

Classes that implement the IPruneEdges plugin interface, as
candidate implementations to whittle the triangulation graph
down to the desired branching network.
'''

from pointsToOutwardDigraph import IPruneEdges
import random
import sys
import os
import itertools
from pygraph.classes.digraph import digraph

#iPruneEdges requires a redef of prune(self, graph) where graph is a pygraph.digraph
#Must modify the graph in place, and is expected to return it

def incident_edges(graph, node):
    neighbors = graph.incidents(node)
    return zip(neighbors, itertools.repeat(node, len(neighbors)))

class nullPruner(IPruneEdges):
    def prune(self, graph):
        return graph

class uniformThroughFour(IPruneEdges):
    #Randomly kick each edge down to an in-degree no greater than 4 but possibly as low as 1.
    #Won't add edges, so nodes with an already-low in-degree are likely to be unaffected.
    def prune(self, graph):
        for node in graph.nodes():
            edges = incident_edges(graph, node)
            edges.sort(key=lambda x: graph.edge_weight(x))
            kill_edges = edges[random.randint(1,4):]
            for foo in kill_edges:
                graph.del_edge(foo) 
        return graph
    
class globalCutoff(IPruneEdges):
    def prune(self, graph):
        must_keep = 0
        for node in graph.nodes():
            try:
                keep_here = min((graph.edge_weight(x) for x in incident_edges(graph, node)))
            except ValueError:
                keep_here = 0
            must_keep = max(keep_here, must_keep)
        iterSafely = graph.edges()[:]
        for edge in iterSafely:
            if graph.edge_weight(edge) > must_keep:
                graph.del_edge(edge) 
        return graph

class minimalistFraction(IPruneEdges):
    """Attempt to keep some particular fractionof edges, but more will be kept.
    This code must never delete the shortest in-edge of a node,
    since we're not trying to make new generators."""
    def __init__(self):
        self.FRAC = 0.65
    def prune(self, graph):
        allWeights = [graph.edge_weight(x) for x in graph.edges()]
        allWeights.sort()
        cutoff = allWeights[int(float(len(allWeights)) * self.FRAC)]
        for node in graph.nodes():
            edges = incident_edges(graph, node)
            edges.sort(key = lambda x : graph.edge_weight(x))
            for x in range(1, len(edges)): #0th element must always survive
                if graph.edge_weight(edges[x]) > cutoff:
                    graph.del_edge(edges[x])
        return graph

class bigDelta(IPruneEdges):
    """Find the biggest jump in incoming edge lengths, and set a cutoff there.
    This might find clusters."""
    def prune(self, graph):
        for node in graph.nodes():
            edges = incident_edges(graph, node)
            edges.sort(key = lambda x: graph.edge_weight(x))
            delta_max = 0.0
            delta_max_index = 1 #never cut off 0 
            edge_lengths = map(graph.edge_weight, edges)
            for x in range(1, len(edge_lengths)):
                delta = edge_lengths[x] - edge_lengths[x-1]
                if delta >= delta_max:
                    delta_max = delta
                    delta_max_index = x
            for killDex in range(delta_max_index, len(edges)):
                graph.del_edge(edges[killDex])
        return graph

CANDIDATE_PRUNERS = [nullPruner(), uniformThroughFour(), globalCutoff(), minimalistFraction(), bigDelta()]

def friendly_rename(graph):
    """
    Builds a new weighted digraph, based on the provided weighted digraph (which isn't modified), 
    which discards all names in favor of alphanumeric node identifiers.
    """
    nextLetter = ord('A')
    nextNumber = 1
    identifierMap = {}
    newGraph = digraph()
    
    for node in graph.nodes():
        if not graph.incidents(node):
            identifier = chr(nextLetter)
            nextLetter += 1
        else:
            identifier = str(nextNumber)
            nextNumber += 1
        newGraph.add_node(identifier, graph.node_attributes(node))
        identifierMap[node] = identifier
    
    for edge in graph.edges():
        weight = graph.edge_weight(edge)
        label = graph.edge_label(edge)
        src = identifierMap[edge[0]]
        dest = identifierMap[edge[1]]
        new_edge = (src, dest)
        attrs = graph.edge_attributes(edge)
        newGraph.add_edge(new_edge, weight, label, attrs)
        
    return newGraph
        
def pruner_bakeoff(nPoints, nSeeds, r0, delta, spread, lumpage, outputNameRoot):
    from spiralPointDistribution import spiralPointDistribution
    from pointsToOutwardDigraph import graphFromPoints
    #import matplotlib.pyplot as plot
    #import matplotlib.tri as tri    
    import pygraph.readwrite.dot as dotIO
    
    points = spiralPointDistribution(nPoints, nSeeds, r0, delta, spread, lumpage)
    
    outdir = os.path.dirname(outputNameRoot)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    #x, y = zip(*points)
    #plot.figure()
    #plot.gca().set_aspect('equal')
    #plot.triplot(tri.Triangulation(x, y), 'r,:')
    #plot.scatter(x, y)
    #plot.show()
    
    #NOT YET FINISHED
    #save png as outputNameRoot.prunerName.png (once I get Python graphviz bindings working)
    
    for pruner in CANDIDATE_PRUNERS:
        graph = graphFromPoints(points, nSeeds)
        graph = friendly_rename(graph)
        graph = pruner.prune(graph)
        dotstring = dotIO.write(graph)
        dotname = "{0}.{1}.gv".format(outputNameRoot, pruner.__class__.__name__)
        with open(dotname, "w") as dotfile:
            dotfile.write(dotstring)

if __name__ == "__main__":
    if len(sys.argv) != 9:
        print "Wrong number of arguments."
        print "nPoints nSeeds r0 delta spread lumpage outputNameRoot numIters"
    
    numIters = int(sys.argv[8])
    for trial in range(numIters):
        thisTrial = sys.argv[7] + str(trial)
        pruner_bakeoff(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), thisTrial)