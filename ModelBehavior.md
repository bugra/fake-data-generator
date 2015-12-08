# Introduction #

To allow for rapid and flexible development of potentially-realistic fake interaction networks, fake-data-generator uses a plugin system to manage the various behaviors that the model can use for each node of the graph.

A behavior is a function that takes some number of inputs (which can be order-sensitive) from other nodes in the graph (or none, for generators), and returns a value. The function is _not_ required to be deterministic. Results will be cached inside the model itself to provide consistent views of nondeterministic functions; the model behavior function doesn't need to implement this itself.

IModelBehavior is the plugin interface defined in model.py. It has four things that must be overridden: two fields and two functions. The fields are implemented as properties in the IModelBehavior base class, but this is an implementation detail used to raise a NotImplemented; derived classes should probably just use values instead.

IModelBehavior objects must have an `__init__` that takes no args other than `self`, due to Yapsy's plugin loading model. For the same reason, only one plugin can exist per file.


# Details #

To write a plugin, create a file that contains exactly one class inheriting from IModelBehavior, then create an appropriate .yapsy-plugin file associated with it, providing metadata and informing the Fake Data Generator that your .py script is, indeed, actually a plugin.

## IModelBehavior requirements ##

Plain `__init__`: If your class has an `__init__` method, it must take no arguments other than `self`.

`calculate`: A function in as many arguments as you'd like. This is the calculation core of your function. Take the arguments, and produce a new value of the same type as a result. While this is typically working entirely in floating-point space, there is no reason you couldn't build a batch of plugins that works only with int, or even string. model.py doesn't typecheck here. However, your IModelBehavior implementation probably shouldn't either- instead, document your type expectations and requirements, and expect the user to load your plugin only alongside other plugins that use the same data type. This function may use `*args`. Keyword arguments will never be passed; all arguments will be passed positionally.

`arity`: A 2-tuple (or other type that can be indexed with `[0]` and `[1]`, but only a 2-tuple is really practical) representing how many inputs your function takes. Especially if you have variable arity due to an `*args` parameter, the model has no way to determine the number of inputs your function can handle. The model generator needs to know this to understand what nodes of the model your function is eligible to be placed in. `[0]` is the (inclusive) lower bound on the number of arguments, and `[1]` is the (inclusive) upper bound, or `None` if your function can handle an infinite number of arguments. Many functions need an exact number of arguments and will thus provide the same value for both. The easiest way to define your arity is by simply assigning a constant 2-tuple of int.

`isNoise`: Will be evaluated for truth. If `true`, then your function is eligible to be selected as a noise function to represent imperfect analysis tools and alter a column before it is printed (but after it has affected later calculations). Set to True only for 1-ary functions that are appropriate for this purpose- most functions will not be.

`generate_name`: A function of the same arity as `calculate`. Takes strings and returns a string. The parameters are the names of the things being provided as input to your calculation function, in the same order the inputs themselves are provided. Your function must generate a descriptive name, dropping the names of the previous levels in to explain the calculation being performed in your `calculate` function. This is used to generate column and GraphViz node names. The parameters may be symbolic or descriptive; if they are nested descriptions from previous levels, they will already be surrounded by parentheses. If your function has a reasonable expression as infix mathematical operations, use that form; express it as a function call only if no better ideas come to mind. (They probably won't in most cases, though.)

## Yapsy plugin requirements ##

Plugin loading is performed via the Yapsy 1.9 plugin framework. (See YapsyFramework for information on installation and usage.) Therefore, each plugin requires a plugin info file. The documentation for these files is [available via Yapsy's docs](http://yapsy.sourceforge.net/PluginManager.html#plugin-info-file-format).

The metadata contained in the `.yapsy-plugin` files is almost unused by fake-data-generator, so automatically generating these files by the batch is a fine strategy, saving a significant amount of time and pointless effort if creating more than one or two IModelBehavior plugins at once. The yapsyPluginInfoEverything script sitting around in the source tree somewhere lets you do exactly this; change its constants to refer to you instead of me.

# Useful "features" #

The way IModelBehavior is used guarantees some behaviors that can be potentially useful- useful enough that IModelBehavior guarantees this. They can be counterintuitive, however.

## One instance per column, plus one ##

To make `__init__` useful, a new copy of your plugin is constructed for every column. (This means that the first one generated is a prototype that will never be assigned directly to any column, so there will be exactly one construction of your class- the first one- that has no associated column.)

This means your `__init__` can do something random and be (reasonably) confident that this will make your plugin behave differently yet consistently for each column it has been assigned to. This permits shenanigans like random but consistent thresholds for modifying or assigning data.

Since the prototype's object `__class__` is getting invoked as a method (which is actually the constructor call), overriding your class's `__new__` will also work as intended.

`arity` and `isNoise` are only checked on the first instance of your plugin created (the one actually created by the plugin manager).

## Stupid arity tricks ##

The `arity` tuple is not bounds-checked, nor is it compared to 1 for `isNoise`. `model.py` makes the (potentially optimistic) assumption that if you have set `isNoise` to `True`, you meant it, and it can safely use your ModelBehavior as a 1ary function to scramble output gently on the last pass.

This means three important things:
  * If you set `isNoise` to `True` on an IModelBehavior that can't handle having exactly one input to `calculate` and `generate_name`, an `arity` that doesn't support 1-ary functions will not save you.
  * If you would like to, for some reason, specify a function that behaves as noise (but not a reasonable model behavior) if it is used in 1-ary mode but some different function (that you do want as a model) with higher arities, you can use `arity` to express only your higher arity range, set `isNoise` to `True` anyway, and then handle the one-parameter case as a noise function. While this is possible, this is pretty stupid and you're better off writing a separate class for the noise.
  * If you would like to specify a function that behaves _only_ as noise, then set `isNoise` to True and specify an arity with a nonsensical range (that does not involve None), wherein the minimum bound value is strictly greater than the maximum bound value. `model.py` doesn't check for this, it simply believes it, and will assign your function to no nodes but may use it as noise anyway. An arity of `(3, 2)` is as equally effective as `(239842, 1)` in getting the point across. If you have a nonsensical arity range and `isNoise` set to `False`, `model.py` will obediently not use your plugin at all. I can think of extremely rare cases where this might be useful and in absolutely all of them there is a better way to do it (generally by editing the source of fake-data-generator).