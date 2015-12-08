# Introduction #

At the top level of the fake-data-generator package, there is a script named fake\_data\_generator.py. It is not designed to be loaded as a module; this is the executable layer executed to produce fake datasets.

# Behavior #

`fake_data_generator`, on each run, produces three files:

  * A .gv file containing a GraphViz representation of the model in DOT format, ready to be rendered
  * A .txt file containing the generated data set
  * A .noisy.txt file containing the generated data set, using random noise functions on each column to simulate imperfect data sampling (see ModelBehavior and how the `isNoise` switch works)

The details of these behaviors are highly configurable.

# Options #

`fake_data_generator.py` has several configuration options. It accepts either a configuration file (in the format used by ConfigParser) or switches on the command line (powered by optparse). Both can be used in tandem; in this case, the configuration file is loaded, then the command line is processed, causing the command line to override the file in case of conflict. This can be used intentionally to override one or two settings in a canned config file.

`fake_data_generator` uses _only_ options for its configuration and has no positional arguments, so this is its entire CLI.

## Command-line-only options ##

This setting cannot be specified in a configuration file, since it doesn't seem useful to let config files chain load each other:

| **Long option name** | **Short option switch** | **Argument** | **Description** |
|:---------------------|:------------------------|:-------------|:----------------|
|--config              |-c                       |A file path   |Load a configuration file. If this switch is present, then before parsing any other options, this file will be loaded and processed by ConfigParser.|

## Output settings ##

These settings (loosely) concern the output format and selection (as opposed to model or graph generation). If using a configuration file, these must be placed in the `[Output]` section.

| **Long option** | **Short option** | **Config var** | **Argument** | **Description** | **Default** |
|:----------------|:-----------------|:---------------|:-------------|:----------------|:------------|
|--output         |-o                |File            |A file path and a filename _with no extension_ or trailing characters|Where fake-data-generator should save its generated data and model (as a GraphViz file). The extension ".txt" is appended for the data file, and ".gv" is appended for the GraphViz file.|(_current directory_)/generatedData|
|--pickRate       |-p                |PickRate        |A float between 0 and 1|The chance that each node in the model should be retained as a column in the output. "0" will produce a highly unexciting data file. The random removal of columns this setting offers models how we cannot necessarily sample every single relevant attribute of a biological system for its interaction network; can our algorithms bridge the gap?|1.0          |
|--tsvRecursion   |-t                |TsvRecursion    |An int        |The depth to which generated column names should be nested within each other. Larger values allow more tracking of what's going on with less cross-referencing, but are harder to read.|3            |
|--graphvizRecursion|-r                |GraphvizRecursion|An int        |The depth to which generated node labels in the GraphViz file should be nested within each other. Larger values allow more immediate viewing of how the model works, but are harder to read and make the graph render physically wider. Because of the visual nature of a GraphViz digraph layout, high values are probably undesirable.|1            |
|--samples        |-m                |Samples         |An int        |The number of samples to draw from the model into the data set- that is, the number of rows of data.|500          |

## Model settings ##

These settings affect the behaviors of the implemented model: what operations may be calculated for each node, and some of the details of pruning the full generated graph down to the model. In a configuration file, these options are in the `[Model]` section.

| **Long option** | **Short option** | **Config var** | **Argument** | **Description** | **Default** |
|:----------------|:-----------------|:---------------|:-------------|:----------------|:------------|
|--behaviors      |-b                |Behaviors       |One or more directory paths, separated with the OS path separator ('`;`' on POSIX systems)|These paths are searched for IModelBehavior plugins, and _all_ of them are loaded as ModelBehavior logic. If you'd like to be more selective, rearrange your plugin directories. This replaces the default ModelBehavior loadout (which is simply implemented with appropriate defaults for this setting), so you'll have to explicitly load the default behaviors if you want them.|`__file__`/../ModelBehavior _(where the defaults live)_|
|--pruner         |-x                |Pruner          |`null`, `uniform`, `fractional`, `globalcutoff`, or `bigdelta`|Choose a pruning algorithm to thin the overly-dense generated graph down to something that looks like an interaction network. **In the future, this will allow loading your own pruner plugin,** but that's not implemented yet. Check source comments for how the five pruners behave. Check `config.py` for the full list of synonyms for the pruner names that are interpreted correctly.|`bigdelta`   |
|--unnoisiness    |-u                |UnNoisiness     |An int        |The number of times to add the identity function to the pool of functions that can be used to add noise to the noisy version of the data set. This represents an increased probability that a column will _not_ be altered (since the identity function returns its argument unchanged). If your selected ModelBehavior plugins include no noise functions (no plugins with `isNoise` set to `True`), this value _must_ be at least 1, or fake-data-generator will crash in the middle of model generation with a ValueError when it tries to pick a noise function to assign to the first column. If you would like every column to be noisy, and you have noise functions available, there's nothing wrong with 0.|3            |

## Graph generation settings ##

These settings affect how the graph is generated before the model is built. Note that several of the settings for SpiralPointDistribution are _not_ exposed here; fidgeting and experimentation has found good calculated defaults. A later version probably should expose these settings; this is still in "late prototype" mode.

If using a configuration file, these settings must be placed in the `[Generation]` section.


| **Long option** | **Short option** | **Config var** | **Argument** | **Description** | **Default** |
|:----------------|:-----------------|:---------------|:-------------|:----------------|:------------|
|--graphs         |-g                |Graphs          |An int        |The number of separate graphs to generate. These graphs are independently generated, but written to the same files, guaranteeing that some columns of the output will be absolutely independent of each other if this setting is higher than 1.|1            |
|--graphSize      |-n                |GraphSize       |An int        |The number of nodes to use per graph. Smaller values tend to produce worse graph shapes, since the graph generation algorithm doesn't get enough of a chance to self-organize. Each node is a potential column in the output.|50           |
|--seeds          |-s                |Seeds           |An int        |The number of "seed nodes" in each graph: nodes with in-degree of 0. Seed nodes will be filled with 0-ary functions, which are generally expected to be random number generators (of varying distributions). These are the "indepdendent variables" of your graph. While any number greater than 0 and smaller than graphSize is valid, values of 2 and 3 are distinctly more likely to produce trivial and non-fully-connected graphs than other values due to how the SpiralPointDistribution operates. This automatically adjusts a few other graph generation parameters to try to create a "good" graph for this number of seeds, at which it is dubiously successful.|4            |