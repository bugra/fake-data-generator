'''
Created on Feb 28, 2012

@author: anorberg
'''

import ConfigParser
import os
import sys

SRC_EXT = ".py"
DEST_EXT = ".yapsy-plugin"

VERSION_NUM = "0.0.1"
WEBSITE = "http://www.systemsbiology.org"
AUTHOR = "Adam B. Norberg"
DESC = "{0] plugin for a computation in the Fake Data Generator. Form letter description not updated."

if __name__ == '__main__':
    cwd = os.path.curdir
    if len(sys.argv) > 1:
        cwd = os.path.dirname(sys.argv[1])
    files = os.listdir(cwd)
    for filePath in files:
        base, ext = os.path.splitext(filePath)
        if ext.lower() == SRC_EXT:
            #generate a file
            infoFilePath = os.path.join(cwd, base+DEST_EXT)
            if os.path.exists(infoFilePath):
                print "Destination file exists, skipping", filePath
                continue
            writeme = ConfigParser.SafeConfigParser()
            writeme.add_section("Documentation")
            writeme.add_section("Core")
            writeme.set("Documentation", "Version", VERSION_NUM)
            writeme.set("Documentation", "Website", WEBSITE)
            writeme.set("Documentation", "Author", AUTHOR)
            writeme.set("Documentation", "Description", DESC.format(base))
            writeme.set("Core", "Module", base)
            writeme.set("Core", "Name", base)
            
            with open(infoFilePath, 'wb') as configfile:
                writeme.write(configfile)
                configfile.flush()
        #end of loop