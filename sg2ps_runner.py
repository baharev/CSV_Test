#!/usr/bin/env python
from __future__ import print_function
import sys
from os import listdir, makedirs
from os.path import dirname, isdir, isfile, join, normcase, normpath, samefile
import shutil

SG2PS_EXE = 'sg2ps'
FLAG =  '--debug'
INPUT_EXT = '.rgf'
RGF_FOLDER = '/home/ali/sg2ps_tests/rgf_folder'

# Create input:
#   Delete TO_COMP folder
#   Copy RGF_FOLDER -> TO_COMP
#   Run sg2ps on TO_COMP
#   Keep only the CSV files
# Invoke csv_test on TO_COMP and ETALON 
#===============================================================================

# A hackish way to import the configuration
sys.path.append(dirname(__file__))
from configuration import ETALON_DIR, TOCOMP_DIR #, EXTENSION

def main():
    if is_there_path_error():
        print('Exiting...')
        return
    print('All paths seem sane')
    # Delete the TOCOMP_DIR as it may contain files from a previous run
    if isdir(TOCOMP_DIR):
        shutil.rmtree(TOCOMP_DIR)        
    makedirs(TOCOMP_DIR)
    # Copy the input files from the RGF folder to the test directory
    to_cp = sorted(f for f in listdir(RGF_FOLDER) if isfile(join(RGF_FOLDER,f)))
    for f in to_cp:
        shutil.copy(join(RGF_FOLDER, f), TOCOMP_DIR)
    print('Copied', len(to_cp), 'files')
    return    
    # FIXME Continue from here: run sg2ps on the TO_COMP folder

def is_there_path_error():
    if not isdir(ETALON_DIR):
        print('ETALON_DIR: not a valid directory path "{}"'.format(ETALON_DIR))
    elif not isdir(RGF_FOLDER):
        print('RGF_FOLDER: not a valid directory path "{}"'.format(RGF_FOLDER))
    elif not isdir(TOCOMP_DIR):
        print('TOCOMP_DIR "{}" will be created'.format(TOCOMP_DIR))
        return False
    # TOCOMP_DIR exists and will be deleted: Check if that can cause data loss        
    elif samefile_or_dir(TOCOMP_DIR, ETALON_DIR):
        print('Etalon and test directory are the same "{}"'.format(ETALON_DIR))
    elif samefile_or_dir(TOCOMP_DIR, RGF_FOLDER):
        print('RGF and test directory are the same: "{}"'.format(RGF_FOLDER))
    elif samefile_or_dir(TOCOMP_DIR, dirname(TOCOMP_DIR)):
        print('Give a non-root TOCOMP_DIR directory: "{}"'.format(TOCOMP_DIR))
    else:
        return False
    return True

def samefile_or_dir(f1, f2):
    try:
        return samefile(f1, f2)
    except AttributeError:
        return normcase(normpath(f1)) == normcase(normpath(f2))

if __name__=='__main__':
    main()
