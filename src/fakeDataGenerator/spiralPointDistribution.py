'''
Created on Jan 25, 2012

@author: anorberg

A module to scatter points in branching, cluster-y shapes. When a Delaunay triangulation
is calculated, the result should be similar to an interaction network graph
once certain edges are pruned.

This strange approach was a desperate effort to come up with some algorithm that produces
a decent interaction-network-shaped graph after many, many failed attempts. It is a
computational simulation of the "draw graph by hand" approach: it puts nodes in cluster-y
shapes, then draws the obvious edges. It is a computational implementation of a
subjective, intuitive, pattern-driven process.

The distressing part is that it works, and I haven't found something better. I would
like to find something better, but this seems not to have happened yet.
'''

from __future__ import division

import blist
slist = blist.sortedlist #convenience namebind
import math
import random
import sys
import itertools
import warnings

#helper math functions
def polarFromCartesian(x, y):
    """
    Calculate polar coordinates from Cartesian coordinates.
    
    Returns an (r, theta) pair.
    """
    r = math.sqrt((x*x) + (y*y))
    theta = math.atan2(y, x)
    return r, theta

def cartesianFromPolar(r, theta):
    """Calculate cartesian coordinates from polar coordinates.
    
    >>> print [round(xy, 3) for xy in cartesianFromPolar(math.sqrt(2), 0.25 * math.pi)]
    [1.0, 1.0]
    
    """
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    return x, y

def radiansFromTurns(turn):
    """Calculate an angle in radians from an angle in turns.
    One turn is equal to 360 degrees, or 2pi radians, or one circle.
    It is an intuitive representation of "fraction of a circle" and is
    used for that reason.
    
    >>> print round(radiansFromTurns(0.5), 2)
    3.14
    
    >>> print round(radiansFromTurns(1), 2)
    6.28
    
    """
    return turn * 2 * math.pi

def turnsFromRadians(rads):
    """Calculate an angle in turns from an angle in radians.
    One turn is equal to 2pi radians, 360 degrees, or one circle.
    
    >>> print round(turnsFromRadians(math.pi), 2)
    0.5
    
    >>> print round(turnsFromRadians(2 * math.pi), 2)
    1.0
    
    >>> print round(turnsFromRadians(0.5 * math.pi), 2)
    0.25
    
    >>> print round(turnsFromRadians(42), 2)
    6.68
    
    """
    return (rads / 2) / math.pi


#TODO: fix doctest to use round
def seed(r, n):
    """Create a ring of points spaced as the corners of a regular n-sided polygon with radius r.
    Return a list of 2-tuples of float that represent these points in 2d, centered on (0, 0).
    
    >>> [[round(bar, 4) for bar in foo] for foo in seed(1, 4)]
    [[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [-0.0, -1.0]]
    
    The negative zero is a detail of the calculation and isn't really to be relied on.
    It's needed for the doctest to work.
    """
    ret = []
    for x in range(0, n):
        theta = radiansFromTurns(x/n) #true division enabled
        ret.append(cartesianFromPolar(r, theta))
    return ret


def distanceCalculator(point):
    """
    Obtain a closure that calculates Euclidean distance between this point and other
    points of the same dimension. The value passed in should probably be frozen-
    because of the closure, strange things may happen if it's modified later,
    depending on the data structures involved.
    """
    def calculateDistance(otherPoint):
        if len(otherPoint) != len(point):
            raise IndexError("Provided point not of same dimension as centroid")
        dsq = 0
        for z1, z2 in itertools.izip(point, otherPoint):
            diff = z1 - z2
            dsq += diff * diff
        return math.sqrt(dsq), otherPoint
    return calculateDistance

def cartesianNearestNeighbors(points, n, point):
    """Brute-force approach to finding the N nearest neighbors of
    a given point, from within an iterable sequence of points.
    
    >>> cartesianNearestNeighbors([(-1,-1),(1,1)], 1, (1,0))
    [(1, 1)]
    
    Results will be sorted closest to furthest:
    
    >>> cartesianNearestNeighbors([(-1,-1),(0,0),(1,1)], 2, (0.75, 0.75))
    [(1, 1), (0, 0)]
    
    If you request more results than there are points, you get all of them and no more:
    
    >>> cartesianNearestNeighbors([(-1,-1),(1,1)], 3, (1,0))
    [(1, 1), (-1, -1)]
    
    You may request no results, and get a list of length zero:
    
    >>> cartesianNearestNeighbors([(-1,-1),(1,1)], 0, (1,0))
    []
    
    """
    
    distAway = distanceCalculator(point)
    nearest = slist((distAway(foo) for foo in points[:n]))
    for foo in points[n:]:
        nearest.add(distAway(foo))
        nearest.pop()
    return [foo[1] for foo in nearest]

def normalizeAngleRadians(angle):
    """Calculate a synonym for the given angle such that -pi <= angle <= pi.
    
    >>> print round(normalizeAngleRadians(2 * math.pi), 6)
    0.0
    
    >>> print round(normalizeAngleRadians(3.5 * math.pi), 4)
    -1.5708
    
    """
    TWO_PI = 2 * math.pi
    while angle > math.pi:
        angle -= TWO_PI
    while angle < -math.pi:
        angle += TWO_PI
    return angle

def normalAngleDifferenceRadians(angleFirst, angleSecond):
    """Calculate the short difference between two angles. -pi/2 <= result <= pi/2.
    
    >>> print round(normalAngleDifferenceRadians(math.pi * 2, 0), 5)
    0.0
    
    >>> print round(normalAngleDifferenceRadians(math.pi/2, 0), 2)
    1.57
    
    >>> print round(normalAngleDifferenceRadians((7*math.pi)/2, 0), 2)
    -1.57
    
    >>> print round(normalAngleDifferenceRadians(1.75*math.pi, -1.75*math.pi), 2)
    -1.57
    
    """
    
    rawDiff = normalizeAngleRadians(angleFirst - angleSecond)
    HALF_PI = math.pi / 2
    if rawDiff < -HALF_PI:
        rawDiff += math.pi
    if rawDiff > HALF_PI:
        rawDiff -= math.pi
    return rawDiff

def lumpyTheta(cartesianPoints, n, r, theta):
    """Calculate a modified theta for a polar point being added to a set to take it closer to existing clusters.
    
    Parameters:
       cartesianPoints- collection of points in (x, y) space to cluster near
       n - number of points to average across for cluster purposes
       r, theta- polar definition of generated candidate point
    Returns:
       new theta to make point a bit more clustery
    
    >>> print lumpyTheta([cartesianFromPolar(0.25, -0.25*math.pi)],1,1,0.25*math.pi) 
    0.0
    
    """
    newPointCartesian = cartesianFromPolar(r, theta)
    nearestCartesian = cartesianNearestNeighbors(cartesianPoints, n, newPointCartesian)
    n = 1+len(nearestCartesian) #in case we got a result that came up short. +1 is for the new point.
    
    newTheta = normalizeAngleRadians(theta)
    for cartesianPoint in nearestCartesian:
        neighborTheta = polarFromCartesian(*cartesianPoint)[1]
        nudge = normalAngleDifferenceRadians(neighborTheta, newTheta)
        newTheta += nudge/n
        
    return newTheta


def spiralPointDistribution(nPoints, nSeeds, r0, delta, spread, lumpage = 2):
    """
    Distribute points in a cluster-y, branching, radial layout designed to create a graph
    shaped like a plausible interaction network after the Delaunay triangulation is
    calculated and "long edges" are pruned. (Determining a "long edge" is solved
    by a different module.)
    
    N "seed" points are arranged along a circle of radius r0 around the origin. Then
    at a radius that increases by delta with every point, M points are placed as follows:
    
    1. A random amount uniformly distributed between 0 and spread is added to the
       theta of the the last plotted point as the new candidate theta. (Spread is
       measured in turns, the angle unit where one turn is a full circle. Radians
       are used internally, but turns are easier to reason about here since the point
       at which points can "come back around" is of specific concern.)
    2. The nearest P points (in Cartesian space, by Euclidean distance) are determined.
       (P = parameter "lumpage". this may be 0.) The theta of these points along with
       the just-calculated random theta is calculated. This is the new theta at which
       the point is actually plotted. This "neighbor-seeking" behavior causes clustering
       behavior with a branch-y shape. Higher values of "lumpage" cause points to
       cluster more since the random component has lower weight, but clusters are
       broader since more points are used to sample a cluster. Experiment to find
       the right value, but experimentation shows 2 to work pretty well.
    3. A point is plotted in polar space at the specified coordinates and added to the
       bottom of the point list. Since the radius increases by a fixed step with each
       point, this puts the list in outwards order, starting from the center (the
       seed points are at the top of the list). This property is required for
       pointsToOutwardDigraph, but can also be enforced by sorting with
       "Euclidean distance from origin" as the sort key. Calculating this is
       a waste of time when it can be guaranteed very easily here.
       
    Parameters:
        nPoints - Total number N of points to generate, including "seed" points
        nSeeds  - Number M of seed points
        r0      - Radius at which to place seeds
        delta   - Step increment of radius on each cycle. Small values relative to r0
                  cause more aggressive clustering relative to original seed positions;
                  large values cause initial seeds to have less influence on the graph shape.
                  This will affect connectivity to the seeds, which will end up the only
                  0-ary "generator" nodes at the top of the acyclic digraph.
        spread  - Range (in turns) for a next theta to be initially chosen, before averaging.
                  This affects the shape of the graph and how far apart clusters tend to be,
                  and thus how likely clusters are to merge or grow together. Parameter
                  must be experimented with.
        lumpage - Number of points used to calculate clustering effects. Large values result
                  in stronger effects of clusters, but clusters are blurrier due to increased
                  influence of nearby clusters near the edges. Small values result in more chaos,
                  but clusters grow together less. 0 results in a completely random point distribution.
                  This value tends to be related to the average in-degree of nodes in the graph
                  under many pruning algorithms, and strongly affects graph shape. Experiment.
    """
    if nPoints < nSeeds:
        raise ValueError("Can't have more seeds than points")
    if nPoints == nSeeds:
        warnings.warn("If nSeeds = nPoints, call to spiralPointDistribution functions as an impractical call to seed")

    points = seed(r0, nSeeds)
    lastTheta = 0
    lastR = r0
    
    while len(points) < nPoints:
        lastR += delta
        lastTheta = normalizeAngleRadians(lastTheta + radiansFromTurns(random.uniform(0,spread)))
        lastTheta = lumpyTheta(points, lumpage, lastR, lastTheta)
        points.append(cartesianFromPolar(lastR, lastTheta))
    
    return points



if __name__ == "__main__":
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "--doctest"):
        #doctest mode
        import doctest
        doctest.testmod(verbose=False)
        sys.exit(0)
    elif len(sys.argv) != 7:
        print "Wrong number of arguments."
        print "Either use no arguments or --doctest for doctests."
        print "Otherwise, arguments are:"
        print "nPoints nSeeds r0 delta spread lumpage"
    
    import matplotlib.pyplot as plot
    import matplotlib.tri as tri    
    
    nPoints = int(sys.argv[1])
    nSeeds = int(sys.argv[2])
    r0 = float(sys.argv[3])
    delta = float(sys.argv[4])
    spread = float(sys.argv[5])
    lumpage = int(sys.argv[6])
    points = spiralPointDistribution(nPoints, nSeeds, r0, delta, spread, lumpage)
    
    x, y = zip(*points)
    plot.figure()
    plot.gca().set_aspect('equal')
    plot.triplot(tri.Triangulation(x, y), 'r,:')
    plot.scatter(x, y)
    plot.show()