# Overview #
This component takes a list of Python scripts to load and search for valid relation operator functions: functions that, by name or decoration, label themselves as relation operations and, when tested, accepting random floats and returning a float. (Tagged functions that do not meet this contract result in warning messages.)

## What's a plugin? ##
A plugin is, in this context, a Python file that is safe for import and provides, when imported, one or more identifiable relation operator functions or function-like objects at the top level of the module. These functions are then taken as candidates to randomly insert as operations performed by the model from the ModelGenerator when deriving data from other data, or when generating data from nothing.

## Why bother? ##
The "relations of interest" problem is very different from the "shape of the relation graph" problem and should be cleanly separated. "Relations of interest" uses a large batch of undifferentiated arbitrary functions, so it is a prime candidate for using a plugin loader. This plugin loader can be relatively clean.

"Relations of interest" is anticipated to have quite a lot of churn, and allowing a plugin model to represent different batches of relation approaches seems reasonable.

# Notes #
`import warnings` for the "not actually a valid plugin" warning messages.

Python code introspection libraries will get you very far here.

# Design #
_module name:_ plugin\_mgmt
## Plugin SPI ##
A plugin is _any callable_ that exists at the top level of the module and begins with rel\_op_. The trailing underscore is required. The loader **must** "test" such callables by extracting the number of parameters the function takes, and filling them with randoms from 0 to 1 . If the result is not a float, or an exception occurs, raise a warning and do not load the function as a plugin.
## Plugin Manager ##_class:_Manager
  * Get random plugin with input n-ary-ness X (or flex) (X may be 0)
  * Get all plugins with input n-ary-ness exactly X (may be 0), None for varargs plugins
  * Load file
  *_No