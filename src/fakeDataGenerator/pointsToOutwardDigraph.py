'''
Created on Jan 27, 2012

@author: anorberg
'''
from __future__ import division
from numpy import array as ndarray
import math
from scipy.spatial import Delaunay
from pygraph.classes.digraph import digraph
import itertools
import yapsy
from yapsy.IPlugin import IPlugin

def euclideanDistance(twople):
    if len(twople) != 2:
        raise ValueError("euclideanDistance must take a 2-item tuple containing numeric sequences of equal length")
    a, b = twople
    if len(a) != len(b):
        raise ValueError("euclideanDistance must take a 2-item tuple containing numeric sequences of equal length")
    
    ssquare = 0.0
    
    for ae, be in zip(a, b):
        diff = ae - be
        ssquare += diff * diff
    
    return math.sqrt(ssquare)

def graphFromTriangulation(triang, nSeeds):
    pointTuples = []
    for point in triang.points: #ndarray
        pointTuples.append(tuple(point))
    
    graph = digraph()
    for index, point in enumerate(pointTuples):
        if index < nSeeds:
            node_color = "red"
        else:
            node_color = "black"
        graph.add_node(point, [("color", node_color)])
    
    for plex in triang.vertices:
        for src, dest in itertools.combinations(plex, 2):
            if src == dest: #no self edges
                continue
            elif src > dest: #all edges point down the list
                src, dest = dest, src;
            
            if dest < nSeeds: #seeds can't have incoming edges
                continue
            
            edge = (pointTuples[src], pointTuples[dest])
            
            if not graph.has_edge(edge):
                graph.add_edge(edge, euclideanDistance(edge))
                
    return graph

def graphFromPoints(points, nSeeds):
    return graphFromTriangulation(Delaunay(ndarray(points)), nSeeds)

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
            identifier = "@" + str(nextNumber)
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

class IPruneEdges(IPlugin):
    def prune(self, graph):
        raise NotImplemented("IPruneEdges is a plugin interface. prune MUST be overridden!")
    

def prunerImplementations(paths):
    """Return an iterable of plugin-info for every locatable implementation of this interface.
    """
    manager = yapsy.PluginManager()
    manager.setPluginPlaces(paths)
    from fakeDataGenerator.pointsToOutwardDigraph import IPruneEdges as foreignPruneEdges
    manager.setCategoriesFilter({
        "PruneEdges" : foreignPruneEdges,                         
        })
    manager.collectPlugins()
    return manager.getPluginsOfCategory("PruneEdges"), manager