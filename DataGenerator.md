# Overview #

The step where data is actually created. This includes column selection and noise insertion.

Column selection is actually the hard part here. Given a model, what data in the model should be exposed in the actual output file?

Data generation from there is easy- repeatedly query the model with no overrides on the input until the requisite number of inputs has been generated, then grab the output from the selected columns and write the data out.

There's no reason to write everything into memory, just write to disk and flush() regularly, since otherwise we're developing memory pressure for no good reason.

# Details #

_package:_ datagen
_function:_ `pickColumns(model)`
_function:_ `generate(model, columns, lines, fuzzVector, ostream)`
The `fuzzVector` parameter is a list of function references of the same length as the columns list. Each element may be None. A None element is replaced with the identity function (`lambda x:x`). That function is applied to the output data when it's taken out of the model, so some degree of noise may be introduced that isn't propagated through the model.