# Overview #

The model generator is the fundamental core of fake-data-generator. It generates the arbitrary relations that will exist in the synthesized data set, which the machine learning algorithms will hopefully be able to pick out again.

## What's a model? ##

In this software, a model is represented as a directed acyclic graph of arbitrary size. The graph is _not_ required to be a single connected region. (In fact, it is better for it _not_ to be fully connected, as independent islands of features are an important test for a machine learning algorithm. Is it incorrectly "bridging the gap"?)

Each node of this graph represents a N-ary function that returns a single floating-point value. Discretization functions that return discrete values within floating-point space are entirely legal. N is the in-degree of the node. Nodes with an in-degree of 0 are independent variables, and are the random source of data; they are either constant or some function of `rand()`, with the latter by far being the most common and useful case.

The model therefore defines all the intended relationships between any two aspects of the data, and provides a computationally-tractable sequence (calculable with topological sort) of operations to generate a row of data. Generating rows independently from new random values for the random independent variables creates a data set.

## What are we generating? ##

Fake, but plausible, data that we know the entire relation-space of.

The graph model described above allows arbitrary relations between arbitrary numbers of factors. Factors are chosen at random (within certain restrictions) to actually be displayed in the output model, so a machine learning algorithm will have to contend with arbitrarily complex indirect links in the data.

These aren't necessarily things we expect an algorithm to reliably be able to pull out. It's necessary for this to be supported, however, to see how far our algorithms can go.

# Assorted Notes #

The "pretty-printing" functions here are actually quite critical to making the system usable. Implementing them is going to be hard.

Graph generation is the area of code that's going to have, by far, the most churn. This code needs to be written clearly and in a heavily-commented way, with as much extract-method-for-code-reuse application as possible. This will make it easier to reorganize the code as experimentation reveals it to be necessary.

# Design #

Documentation here is a supplement to, not a replacement for, the PyDoc. Read both. This is more about when one would use these entry points than how to use them.

_primary module_: model
_secondary packages_: spiralPointDistribution, pointsToOutwardDigraph

## model.py ##
### Node class ###
_class_: Node. Represents one calculation node of the model. Stores a function, but only has a value in the context of a query to the model. Externally useful primarily for traversing the shape of the model (which will be necessary for the Column Picker to pick columns), rendering/printing/describing the model, or as a key to pick results out of a Model query. As such, Node is stably hashable- but due to its "position-in-a-graph"-based nature, this hash is purely by object identity.

_Initializer_: If you're building a graph in top-down order, the initializer helps you out- it takes an iterable of other Node objects as parent nodes. It also updates those nodes automatically to represent a link to this object. In all cases, you must provide a name, and an IModelBehavior to act with, and optionally another one as noise. All these attributes can be changed later, but the initializer is the "supported" route.

_Private method_ `_addOut`: Appends a given node to the output list (the outwards-facing adjacency list) for this node, then returns `self`. The self-return property is used in list comprehensions in a few spots, most notabily in the initializer.

_Method_ `addEdge`: Adds a new edge from this node to another one. This updates both this node's list of outputs and the destination node's list of inputs, which is how it differs from `_addOut`, above.

_Method_ `removeEdge`: Removes an edge from this mode to another one. If no such edge exists, returns False. Otherwise, removes the reference from both lists and returns True. Since edges are stored in a list, this operation requires a list iteration and midpoint update and is slow for nodes with a very large number of edges. (Large numbers of edges are not really anticipated.)

_Method_ `calculate`: Calculates the value for this node, recursively querying parent nodes until a root or cached value is encountered. A cache key must be provided, since cache behavior is forced. Some nodes may have partially- or wholly-randomized operation, so value caching is required to provide consistent behavior. If this value has already been cached, this is simply a dict lookup; otherwise, it may traverse the entire graph upwards. It is impossible for this to be worse than querying every node in the graph, since values _are_ cached, bounding this at O(n) performance in the count of nodes in the graph. Furthermore, a sequence of queries over all _n_ nodes using the same key is _also_ bounded at total sum time O(n) since no calculation will be repeated; each node will be calculated exactly once. Assign the time cost of "querying upwards" for input data to the node requesting upwards and this finding becomes more obvious.

_Method_ `columnValue`: Similar to `calculate`, but also applies the noise function to the output. Noise functions are not propagated between nodes, since they represent errors in _measurement_, not random factors in the underlying process. **This value is not cached, so subsequent calls may give inconsistent values** if the noise function is random. The expected use case is that all values will be iterated over exactly once per line, so no caching is appropriate. An unnecessary cache is just a fancy memory leak, so no cache is implemented. (So is a cache with bad policy, such as the one used in the `calculate` method. Calculate is caching for correctness, not performance, but unless we really need to archive the world, we should revisit that design the moment we start having perf issues.)

_Method_  `genName`: Generate a description of what this node does, nesting names to a given recursion depth. The "first" flag shouldn't be played with under most circumstances- it simply sets up a special case for generator nodes, which need to behave differently in name display. This relies on the `generate_name` method of IModelBehavior, and will fail if the underlying behavior function hasn't been initialized. (You're supposed to provide it in the initializer.) This method doesn't cache anything- it probably should cache a different string for each remainingRecursion level, but so far this hasn't been enough of a performance impact to justify the trouble.

_Method_ `toGraphViz`: Generates the GraphViz statement for this node, and for all the edges _incoming into_ this node.

_Method_ `__str__`: Yields a friendly debugging string. Not really usable for much of anything else.

_Private method_ `_updateReachableSingle`: One iteration of transitive reachability calculations.

_Method_ `updateReachable`: Updates the set of nodes that can be reached by this one. A part of cycle detection and break detection algorithms that are no longer actually in use- RemovedFromModel.txt has some historical code that used to care about these. This should probably be removed from the code as well, except we may play with it later.

## Class IModelBehavior ##

IModelBehavior is the ModelBehavior plugin interface; please see documentation on its own page. This class, as written, _does_ nothing and must be extended; all methods raise `NotImplemented`.

## Things not in classes ##

_Function_ `graphvizEntireThing`: Given the head nodes (the 0-ary nodes) of a graph, get a String giving a GraphViz representation of the graph. Sort of inefficient, and I should rewrite it better since GraphViz isn't sensitive to the order statements are provided in, while this tried to provide some strict guarantees that are utterly unnecessary.

_Function_ `modelBehaviorImplementations`: An implementation of canned logic to load all ModelBehavior plugins identified from a list of given paths. Uses Yapsy's plugin loading API in its obvious ways. Does a weird self-import for reasons related to Python's schizophrenic handling of the `__main__` module.



## spiralPointDistribution.py ##

## pointsToOutwardDigraph.py ##