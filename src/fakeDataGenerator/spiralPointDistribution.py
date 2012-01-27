'''
Created on Jan 25, 2012

@author: anorberg
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


def spiralPointDistribution(nPoints, nSeeds, r0, delta, spread, lumpage = 3):
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