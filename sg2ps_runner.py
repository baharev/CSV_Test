#!/usr/bin/env python
from __future__ import print_function
import sys
from os import listdir, makedirs, remove
from os.path import dirname, isdir, join

SG2PS_EXE = 'sg2ps'
FLAG =  '--debug'
INPUT_EXTENSION = '.rgf'

#===============================================================================

# A hackish way to import the configuration
sys.path.append(dirname(__file__))
from configuration import ETALON_DIR, TOCOMP_DIR, EXTENSION

def main():
    
    if ETALON_DIR == TOCOMP_DIR:
        print('Etalon and test directory are the same:', ETALON_DIR)
        return
    
    # FIXME Continue from here
    # Delete the to comp dir and copy .rgf, .set and .xy files into the test dir?
    # Or simply write the test dir over with the etalon dir?
    #
    # clean up csv files from the previous run, if any
    to_del = sorted(f for f in listdir(TOCOMP_DIR) if f.endswith(EXTENSION))
    for f in to_del:
        remove(join(TOCOMP_DIR,f))
    if to_del:
        print('Deleted',len(to_del),'files in', TOCOMP_DIR)
    # the check is necessary, otherwise makedirs throws if the dir exits
    if not isdir(TOCOMP_DIR):
        makedirs(TOCOMP_DIR)
    

if __name__=='__main__':
    main()
