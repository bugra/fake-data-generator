

# Overview #

Generating a random graph that is shaped vaguely like a plausible genomic interaction network is a hard problem because it is very poorly specified. Mathematically, what "looks like an interaction network"? The properties of appropriate graphs are mostly subjective, hard to quantify, and most plausible guesses turn out to be wrong.

While there is a wide variety of canned random graph generation algorithms, the graphs they produce are generally inappropriate, due to having the wrong shape. Algorithms that are carefully tuned to make guarantees about uniform distribution of graph shapes are, categorically, not optimized for this space.

A desperate attempt to get a working algorithm by computationally simulating the process of drawing circles on a sheet of paper and drawing edges between them and calling it a graph turns out to be the most effective algorithm of many tried, even though this causes what would ideally be a completely abstract graph algorithm to ricochet off computational geometry in the process.

# Approach #

The algorithm that became the Spiral Point Distribution came after several unsuccessful designs for an algorithm defined purely by abstract graph theory. With no mathematical definition of a "good" graph forthcoming, and no success in defining one, developing an algorithm was purely a guessing game.

With no success in abstract algorithms, I contemplated how, would, by hand, draw "something that looks like an interaction network." I came up with a sequence of steps like this:

  1. Draw circles in sort of cluster-y chain-like ways.
  1. Draw arrows between them that follow those paths and put crosslinks within clusters.
  1. Don't create any cycles.

This is very much an "I know it when I see it" thing. But if attempts to mathematically create a graph with similar properties weren't working, what if I wrote a program to do exactly this?

Now I had three different problems to solve, one of which was very easy- once I had the general shape right, making sure the graph was acyclic would be the simplest. What would put the nodes "in the right spot", and "draw edges" between them?

## Placing points ##

Since I'm abstracting the problem to something where nodes have a _position_, then the most sensible way to represent one is a two-dimensional point. To assign them in random, but cluster-forming ways that also tend to form chains, I opted to place them in a circular pattern with a steadily-increasing radius. This also solved the "acyclic graph" problem: make all edges point "outwards" and no cycles can form.

To cause clusters, instead of placing points randomly on the circle, I initially chose random angles at the current radius, found the geometrically nearest points, and adjusted the angle to be the average of the random angle and the points that wound up nearest. This approach leads to loose, meandering, branching clusters, which is exactly the pattern desired.

## Drawing lines ##

A Delaunay triangulation provides a good start at connecting the nodes together. However, this provides too many edges; points that are apparently part of different groups and should be treated as such are bound together, since they are still "next to" each other in terms of region adjacency.

Triangulating the region and then trimming out "long" edges was the order of the day. The Delaunay triangulation was converted to a directed graph with edges pointing outwards from the center, and edge weights equal to the Euclidean distance between nodes. This is where GraphPruning algorithms begin: finding edges that "should be" trimmed off the graph.

Several pruning strategies have been tried, and three of them have been found to work acceptably; there's room for improvement in pruners, but the foundation seems sound.

# Algorithm #

The Spiral Point Distribution algorithm plots points in polar coordinates (converting between turns and radians because this actually results in the most practical function interface), but stores them in rectangular (Cartesian) coordinates for ease of nearest-neighbor and Euclidean distance calculation. It eventually outputs the set of points; the triangulation and conversion to a graph technically happens in a different module, although it's closely related.

## Inputs ##

The Spiral Point Distribution takes six parameters. It is not a "true" mathematical function, since its behavior is randomized; calls with identical parameters will almost never produce identical results.

  * **_nPoints_ --** Total number of points to generate (including seeds).
  * **_nSeeds_ --** Number of points to place in the center circle, which will become the 0-ary "generator" nodes of the graph in the output
  * **_r0_ --** Radius of the starting circle around which the seeds are evenly placed
  * **_delta_ --** Amount to increase the radius by for each point
  * **_spread_ --** Range, measured in turns (fractions of a full circle), for random generation of next angle
  * **_z_ --** Number of points to grab for clustering behavior


## Output ##

A list of points, represented as 2-tuples of float (representing x,y coordinates).

The first _nSeeds_ of these points are arranged in a circle around the origin (0, 0), and the remainder of the list is in strictly increasing radius from the origin. The points will follow the clustered pattern typical of this algorithm.

## Method ##

With variable names as listed above for inputs, the exact algorithm is as follows, in pseudocode:

```
function spiralPointDistribution:
    #sanity checks
    assert nSeeds >= nPoints
    warn if nSeeds == nPoints

    ret = list containing nSeeds points arranged in an r0-radius circle around the origin

    theta = 0
    r = r0

    while (length of ret) < nPoints:
        increment r by delta
        add a random angle between 0 and spread to theta
        calculate Cartesian coordinates (x, y) from polar coordinates (r, theta)
        closestZ = the closest z points in ret to (x, y)
        allThetas = list of all angles in closestZ
        append theta to allThetas
        theta = mean(allThetas)
        recalculate (x, y) from (r, theta) #with theta updated
        append (x, y) to ret
    end while

    return ret
end function
```

Note that ret is storing values in Cartesian space, although many of the operations are polar. A strong argument can be made for storing ret as (x, y, theta) inside the function, then returning a list made from the (x, y) of ret to avoid several avoidable Cartesian-to-polar conversions. This is an implementation detail and can be revisited at any time.

The Python source is not especially different from or especially less legible than the pseudocode written here. Python is like that.

# Weaknesses #

## Few seeds ##

spiralPointDistribution has trouble with 3 seeds, and is almost useless with 2 seeds. To produce a sane interaction network, the independent variables (the seeds, which become generators) need to interact in some way. With fewer seeds, the positioning at further-distant angles causes the points to take a longer time to converge. Increasing the number of seeds will generally increase the connectivity of the graph, rather than partition it into subtrees that take a longer time to converge.

The severity of this problem can be mitigated somewhat by choosing a value for delta that is large relative to [r0](https://code.google.com/p/fake-data-generator/source/detail?r=0).

## Few nodes ##

The patterns created by spiralPointDistribution become clearer when they get some small amount of time to converge. Too few nodes will often also result in a degenerate graph that, after pruning, is tree-shaped or, worse, shaped like a linked list.

There's no automated way currently written to test for graph degeneratices. Pay attention to the rendered graphs; if a model comes out fundamentally bogus, throw it out and spin again.

# Tweakable Knobs #

All of the input parameters to the function can be altered theoretically independently. _nPoints_ and _nSeeds_ are fundamental to the properties desired of the graph and are the primary settings; the other four settings are to shape the graph and build it as desired.

The limited range for angles provided by _spread_ prevents chaos in the first few points from overwhelming cluster-shaped behavior and prevent branching-tree behavior from the outset. Values greater than 1 are not entirely senseless, as this results in angles that can be anywhere on the circle but are more likely to be in a fixed range. This is not a very precise mechanism, however. While this is the parameter that has the least effect on graph generation, it does have enough effects to be worth experimenting with. _Very low values will lock the generator and should be avoided._ Averaging makes it possible for a point to "go backwards" around the circle relative to the previous point; it is possible for a small _spread_ to result in the generator getting unavoidably "dragged back" to a single uneven column of points or a single cluster, causing a highly degenerate graph.

_r0_ and _delta_ aren't really independent of each other; they are meaningful mostly as a ratio. The heavier the ratio is towards _r0_, the more the initial point placements will be separated spatially. High _r0_ results in graphs that are shaped approximately like trees for the first few "layers", and this separation increases with higher _r0_. Increasing _delta_ (or decreasing _r0_) therefore helps mitigate problems caused by a low number of seeds. Note that a graph with 1 seed does not generally degenerate, since the degeneracies are all related to insufficient connection between generators, and one generator can't expect any such interactions anyway.

_z_, the cluster smoothing factor, has the strongest impact on graph shape. A value of 0 discards most of the algorithm and results in an unorganized point cloud, although _spread_ causes a generally spiral shape (especially at low values). Higher values create broad clusters that do not diverge or reshape significantly as more points are plotted. Values between 2 and 4 seem to work best for creating complex interaction networks. 1 is almost a special case, and creates a heavily-branching, web-like pattern with distinctly different properties that may be worth investigating as an alternate generator. Describing the shape of the graphs remains difficult; experimentation is encouraged.