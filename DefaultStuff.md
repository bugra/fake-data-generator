# Overview #

All behaviors of the model are implemented as IModelBehavior plugins, in the ModelBehaviors package.

# Operations to Support #

Operations are sorted by arity- the number of input values they take. Some functions are of variable arity- having at least one varargs function is required for the model generator to reliably function.

## 0ary ##
  * uniform 0-1
  * Gaussian mean 0.5 stddev 0.3
  * coin toss
==1ary==1
  * Discretize
  * Gaussian noise
  * Log transform
  * Negate
  * 1-x (equivalent to 1 + negate)
  * Reciprocal
  * 0-1 floating point truncation
## 2ary ##
  * absDiff
  * cmp
  * mult
  * smallRatio
## varargs ##
  * Sum
  * Average
  * Max
  * Min
  * To add: stddev
  * To add: range