# Introduction #

To smoke test and experiment with implementation during development, some classes were given if-name-equals-`__main__` regions that are not expected to be part of any final pipeline or tool system.

Because it may be useful to repeat these tests, these alternate entry points are listed here.

# Modules with Alternate Entry Points #

## model ##

The entry point in `model` is the present CrudePrototype of the system. `model.py` as a script takes no parameters and behaves as follows:

  1. Build a random model of size 50 with the default plugins and construction settings I found to work reasonably well (see the file itself for details)
  1. Write a GraphViz-formatted DOT file to `E:\debris\whatever.gv`, which refers to the scratch space on the large hard drive on my dev box. Someone running this will almost certainly need to change this path; alter line 407.
  1. Write a fake data file to `E:\debris\fakeData.tsv`, formatted like an Excel output text data file. The first line of this file is a (highly, if tersely, descriptive) header; subsequent lines are data generated as per the model data generation algorithm. This data is **not** subject to noise. This file contains 200 samples; change line 414 to alter this count.

This is very similar to the final output format expected by the tool- a Graphviz diagram alongside a fake dataset.

## candidate\_test\_pruners ##

This entire file, as it stands, is for testing purposes; the pruners will wind up split out into plugins soon. As a script, this module generates some number of graphs, prunes a copy of each graph with each pruner listed in the code, and saves the results as GraphViz files. This exists to allow discussion and evaluation of the different pruning strategies.

The script requires eight parameters (yikes!), six of which specify parameters for graph generation, one of which is the root of output destinations, one of which specifies the number of trials:

|**Position**|**Name**|**Description**|
|:-----------|:-------|:--------------|
|1           |nPoints |Number of nodes in each generated graph.|
|2           |nSeeds  |Number of 0-ary nodes (roots) of each graph.|
|3           |[r0](https://code.google.com/p/fake-data-generator/source/detail?r=0)|A floating point value that affects the degree to which the starting points "split" the graph.|
|4           |delta   |A floating point value that affects the shape of clusters in the graph and the way it splays.|
|5           |spread  |A floating-point value between 0 and 1 that affects how many clusters are formed.|
|6           |lumpage |An integer between 0 and nSeeds that affects how points are placed in clusters.|
|7           |outputNameRoot|A string representing a directory path and filename prefix. This will be string-suffixed with the name of the pruner, the number of the trial, and the ".gv" GraphViz file extension to save the result tables.|
|8           |nTrials |An integer representing how many graphs to generate, prune, and save.|

Parameters 1-6 are passed to the SpiralPointDistribution module, which is the core of how this software generates interaction-network-shaped graphs. The description of the parameters is sketchy because the entire algorithm is sketchy. Please see its page for more details.

## spiralPointDistribution ##

The entry point in `spiralPointDistribution.py` tests the first stage of model generation: the computational geometry step where a clustered pattern of points (in cartesian space, generated primarily by polar math) is built, then triangulated. (`pointsToOutwardDigraph.py` converts this triangulation into an abstract graph.)

Run as a script, it does one of two things:
  * Runs doctests on the helper functions in the module.
  * Generates a point distribution and uses matplotlib to draw it, as well as its triangulation.

To run the doctests, use the `--doctest` flag.

Generting a distribution requires six parameters:

|**Position**|**Name**|**Description**|
|:-----------|:-------|:--------------|
|1           |nPoints |Number of nodes in each generated graph.|
|2           |nSeeds  |Number of 0-ary nodes (roots) of each graph.|
|3           |[r0](https://code.google.com/p/fake-data-generator/source/detail?r=0)|A floating point value that affects the degree to which the starting points "split" the graph.|
|4           |delta   |A floating point value that affects the shape of clusters in the graph and the way it splays.|
|5           |spread  |A floating-point value between 0 and 1 that affects how many clusters are formed.|
|6           |lumpage |An integer between 0 and nSeeds that affects how points are placed in clusters.|

If run with these parameters, the program will draw a plot of the points with its triangulation overlaid. This can be saved to a file. This entry point is _very_ useful for experimenting with point generation settings to see the sorts of graph shapes it might inspire and will probably remain.


## Several modules in ModelBehaviors ##

The following IModelBehavior plugins in the ModelBehaviors package run doctests when invoked:

  * negate\_1noise
  * zeroOne\_truncate\_1noise

Many others have doctest-launching `__main__` blocks, but no actual doctests.

# Scripts that are special tools #

## results2dot ##

This is a brief script I wrote to see if there are intelligible patterns in RF-ACE output of a tractable size if plotted using GraphViz. Answer: Not really. This just reformats TSVs that contain a reasonable definition of sources and destinations into an equivalent GraphViz file.

## yapsyPluginInfoEverything ##

This is a brief script that creates a crude yapsy-plugin file for every .py file in the current directory. This is an immense time-saver when composing a large batch of tiny plugins, such as for a family of IModelBehavior objects.

If run with a parameter, it interprets that as a directory and scans it. If there is no parameter, it uses the current working directory. If you'd like different author/description/website strings, change the constants in the file.

# Modules notably lacking an alternate entry point #

Some modules seem like they should or probably actually should have a test or submodule entry point, but don't:

## pointsToOutwardDigraph ##
Test code that isolates this logic from the spiralPointGenerator would be nice, but the two classes are actually very closely linked. Manually creating a useful set of test points is a time cost I haven't paid yet.