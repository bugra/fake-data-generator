# Purpose #
Machine learning algorithms mining for _patterns_ are difficult to evaluate. The sweeping majority of test data sets either come from real-world observations, or are incredibly trivial; it is hard to find a high-quality artificial data-set designed to express nontrivial relations. The Fake Data Generator is intended to be a high-quality source of fake data with known patterns.

Known patterns provide a "correct answer" for such machine learning algorithms. Real data could always have unknown relationships that simply hadn't been noticed before, so a spurious relationship requires significant investigation before concluding that an algorithm is ineffective. If a data set has been generated from a fully known semi-deterministic conditional model, spurious relationships of various degrees can be confidently and definitively isolated.

This both tests correctness of an algorithm and tests its behavior; theories about the cause of unusual behavior of a machine learning algorithm can be evaluated by synthesizing fake data sets that exhibit that cause and the behavior of the algorithm can simply be observed from that set.

# Features #
The following features are intended for the software:
  * Generate a large table of data representing complex relations with some hidden stages and at least one hidden independent variable
  * Customizable output length
  * Legible representation of complete model
  * Save a model for later in machine-readable format, load a previously-generated model
  * Customizable parameters for column selection
  * Variable complexity of model
  * Future version: Read a human-writable "model definition file" to create data off a fixed model

# Modules/Architecture #
The following chunks are probably going to wind up in separate Python files and can be developed semi-separately:
  * ModelGenerator, which is based on this weird SpiralPointDistribution algorithm
  * PluginEngine to import modules specially designed as Stuff The Model Can Do
  * DefaultStuff The Model Can Do
  * EntryPoint, which also processes the command line and saves output, as a thin script around data generation APIs
  * ModelSaveLoad
  * Future work: ModelSpecReader