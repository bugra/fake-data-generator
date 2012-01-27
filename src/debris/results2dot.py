'''
Created on Jan 24, 2012

@author: anorberg
'''

import csv
import sys


MIRN = ':MIRN:'

if __name__ == "__main__":
    source = open(sys.argv[1], "rb")
    fromCol = int(sys.argv[2])
    toCol = int(sys.argv[3])
    table = csv.reader(source, dialect=csv.excel_tab)
    
    print "digraph Relations{"
    
    for row in table:
        #strip MIRN relations
        src = row[fromCol]
        dest = row[toCol]
        if (src.find(MIRN) < 0) and (dest.find(MIRN) < 0):
            print '"' + row[fromCol] + '"->"' + row[toCol] + '"'
    
    print "}"
    
