_This page was last updated on March 2, 2012, and refers to code revision a6d454ada79b._

  * This version has a working, crude prototype of the generation system. Currently, it has no user interface- to change its settings, including input and output paths (which are tuned to my dev box), modifying the source is required. This is a crude proof-of-concept to verify that the engine works before hanging anything else off it. That said, it does work.
  * GraphViz output isn't quite the way I want it. I've done something wrong with the Color parameter.
  * Pruners haven't yet been converted into plugins. Since pruning strategy is definitely a matter of opinion, this should happen even for the basic pruners already defined.
  * The entire codebase needs a third-party refactor. The architecture is dubious and awkward, but I'm too entrenched in it to understand what would improve it. Feedback would be greatly appreciated.
  * The generation code is much faster than I expected. Key cacheing works correctly and uneventfully.
  * The scatter range on the Gaussian fuzz 1-ary operator should probably be changed.
  * Most of the 1-ary operators pretty much suck. More that introduce random noise need to be introduced.
  * No "column censorer" has been developed yet. That should happen, possibly still within the proof-of-concept stage.