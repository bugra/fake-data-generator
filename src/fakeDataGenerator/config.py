'''
Created on Mar 7, 2012

@author: anorberg
'''

import os.path
import sys
import candidate_test_pruners
import optparse
import ConfigParser

NULL = candidate_test_pruners.nullPruner()
UNIFOUR = candidate_test_pruners.uniformThroughFour()
GLOBALCUT = candidate_test_pruners.globalCutoff()
MINFRAC = candidate_test_pruners.minimalistFraction()
BIGDELTA = candidate_test_pruners.bigDelta()

PRUNER_LUT={
                "null":NULL,
                "nullpruner":NULL,
                "uniform":UNIFOUR,
                "uniformthroughfour":UNIFOUR,
                "minfrac":MINFRAC,
                "minimalist":MINFRAC,
                "fraction":MINFRAC,
                "fractional":MINFRAC,
                "minimalistfraction":MINFRAC,
                "delta":BIGDELTA,
                "bigdelta":BIGDELTA
            }

class Config(object):
    '''
    A struct-like class that holds the configuration for the fake data generator.
    Designed to build itself from a command line and/or a config file.
    '''

    outputRoot = os.path.join(os.path.curdir, "generatedData")
    nGraphs = 1
    graphSize = 50
    nSeeds = 4
    gvRecursion = 1
    tsvRecursion = 3
    tsvColRate = 1.0
    behaviorPaths = [os.path.join(os.path.dirname(__file__), "..", "ModelBehaviors")]
    pruner = candidate_test_pruners.bigDelta()
    samples = 500

    def __init__(self, relevant_argv=None):
        '''
        Constructor. Read settings out of relevant_argv with optparse, gating to ConfigParser in case of the --config option
        '''
        if relevant_argv is None:
            relevant_argv = sys.argv[1:]
        
        parser = optparse.OptionParser()
        parser.add_option("-c", "--config", dest="configFile", help="Load a configuration file")
        parser.add_option("-g", "--graphs", dest="graphs", type="int", help="Number of separate graphs to generate")
        parser.add_option("-n", "--graphSize", dest="graphSize", type="int", help="Number of nodes per graph (including seeds)")
        parser.add_option("-s", "--seeds", dest="seeds", type="int", help="Number of seeds per graph")
        parser.add_option("-r", "--graphvizRecursion", dest="gvRecursion", type="int", help="Depth of recursion for procedural name generation in Graphviz diagram")
        parser.add_option("-t", "--tsvRecursion", dest="tsvRecursion", type="int", help="Depth of recursion for name generation in generated data file")
        parser.add_option("-p", "--pickRate", dest="pickRate", type="float", help="Fraction of nodes to place in the output file; selected randomly")
        parser.add_option("-b", "--behaviors", dest="behaviors", help="Paths to search (use OS path separator) for behavior plugins")
        parser.add_option("-x", "--pruner", dest="pruner", help="Name of graph pruning algorithm to use")
        parser.add_option("-m", "--samples", dest="samples", type="int", help="Number of rows of data to output")
        parser.add_option("-o", "--output", dest="outputRoot", help="Output file name without extension; .gv or .txt will be appended")
        
        (options, args) = parser.parse_args(relevant_argv)
        
        if options.configFile:
            self._parse_config_file(options.configFile)
        #all settings on the CLI override settings in the file, so just blindly write from here on out
        
        if options.graphs:
            self.nGraphs = options.graphs
        
        if options.graphSize:
            self.graphSize = options.graphSize
        
        if options.seeds:
            self.nSeeds = options.seeds
        
        if options.samples:
            self.samples = options.samples
        
        if options.gvRecursion is not None:
            #because zero is a legal value
            self.gvRecursion = options.gvRecursion
        
        if options.tsvRecursion is not None:
            self.tsvRecursion = options.tsvRecursion
            
        if options.pickRate is not None:
            self.tsvColRate = options.pickRate
            
        if options.behaviors:
            self.behaviorPaths = options.behaviors.split(os.path.pathsep)
            
        if options.pruner:
            self.pruner = PRUNER_LUT[options.pruner.lower()]
        
        if options.outputRoot:
            self.outputRoot = options.outputRoot
    def _parse_config_file(self, filePath):
        """
        Use a ConfigParser to load settings.
        """
        parser = ConfigParser.SafeConfigParser(
                {
                    "File":self.outputRoot,
                    "PickRate":self.tsvColRate,
                    "TsvRecursion":self.tsvRecursion,
                    "GraphvizRecursion":self.gvRecursion,
                    "Behaviors":self.behaviorPaths,
                    "Pruner":self.pruner,
                    "Graphs":self.nGraphs,
                    "GraphSize":self.graphSize,
                    "Seeds":self.nSeeds,
                    "Samples":self.samples
                }
            )
        parser.add_section("Output")
        parser.add_section("Model")
        parser.add_section("Generation")
        
        parser.read(filePath)
        
        self.outputRoot = parser.get("Output", "File")
        self.tsvColRate = parser.getfloat("Output", "PickRate")
        self.tsvRecursion = parser.getint("Output", "TsvRecursion")
        self.gvRecursion = parser.getint("Output", "GraphvizRecursion")
        self.samples = parser.getint("Output", "Samples")
        
        self.behaviorPaths = parser.get("Model", "Behaviors").split(os.path.pathsep)
        self.pruner = PRUNER_LUT[parser.get("Model", "Pruner").lower()]
        #TODO: special resolution against canned pruners for now
        
        self.nGraphs = parser.getint("Generation", "Graphs")
        self.graphSize = parser.getint("Generation", "GraphSize")
        self.nSeeds = parser.getint("Generation", "Seeds") 