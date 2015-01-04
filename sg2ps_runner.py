#!/usr/bin/env python
from __future__ import print_function
import subprocess
import sys
from os import access, listdir, makedirs, remove, X_OK
from os.path import dirname, isdir, isfile, join, normcase, normpath, samefile
import shutil

#===============================================================================

SG2PS_EXE = '/home/ali/ws-pydev/CSV_Test/sg2ps'
FLAG =  '--debug'
INPUT_EXT = '.rgf'
RGF_FOLDER = '/home/ali/sg2ps_tests/rgf_folder'

# TODO Invoke csv_test on TO_COMP and ETALON 
#===============================================================================

# A hackish way to import the configuration
sys.path.append(dirname(__file__))
from configuration import ETALON_DIR, TOCOMP_DIR, EXTENSION

def main():
    if is_there_path_error():
        print('Exiting...')
        return
    print('All paths seem sane')
    # Delete the TOCOMP_DIR as it may contain files from a previous run
    if isdir(TOCOMP_DIR):
        shutil.rmtree(TOCOMP_DIR)        
    makedirs(TOCOMP_DIR)
    # Copy the input files from the RGF folder to the test directory TOCOMP_DIR
    to_cp = sorted(f for f in listdir(RGF_FOLDER) if isfile(join(RGF_FOLDER,f)))
    for f in to_cp:
        shutil.copy(join(RGF_FOLDER, f), TOCOMP_DIR)
    print('Copied', len(to_cp), 'files')
    # Run the sg2ps executable on the projects in TOCOMP_DIR  
    projects = [f[:-len(INPUT_EXT)] for f in to_cp if f.endswith(INPUT_EXT)]
    for f in projects:
        print('Processing:', f)
        ret = subprocess.call([SG2PS_EXE, FLAG, f], cwd=TOCOMP_DIR)
        if ret:
            print('Fatal error when calling {}, exiting...'.format(SG2PS_EXE))
            return
    print('Test file generation finished')
    # Keep only the result files
    to_del = sorted(f for f in listdir(TOCOMP_DIR) if not f.endswith(EXTENSION))
    for f in to_del:
        remove(join(TOCOMP_DIR, f))

def is_there_path_error():
    # Consider replacing this long if - elif with a loop
    if not isfile(SG2PS_EXE) or not access(SG2PS_EXE, X_OK):
        print('SG2PS is not executable, check: "{}"'.format(SG2PS_EXE))
    elif not isdir(ETALON_DIR):
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
