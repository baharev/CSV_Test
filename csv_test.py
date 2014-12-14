from __future__ import print_function
import codecs
from os import listdir, makedirs
from os.path import isdir, join
from shutil import rmtree

ERRORS_DIR = '/tmp/sg2ps_tests/result'
ETALON_DIR = '/home/ali/sg2ps_tests/etalon'
TOCOMP_DIR = '/home/ali/sg2ps_tests/to_compare'
EXTENSION  = '.csv'
SEP  = ','
TO_TYPE = { 's' : str,
            'i' : int,
            'd' : float,
          }
ENCODING = 'ascii'

def main():
    setup_errors_dir()
    etalon_filenames = get_all_filenames(ETALON_DIR, EXTENSION)
    for etalon in etalon_filenames:
        check_file(etalon)

def check_file(filename):
    header, lines = read_csv(filename)
    col_types = get_col_types(header)
    if col_types is None:
        return
    # check row length!!!
    type_errors, table = convert(col_types, lines)
    if type_errors:
        write_cell_errors(filename, header, lines, type_errors)
        return
    return table
       
#-------------------------------------------------------------------------------

def setup_errors_dir():
    if isdir(ERRORS_DIR):
        rmtree(ERRORS_DIR)
    makedirs(ERRORS_DIR)

def get_all_filenames(directory, extension):
    files = sorted(f for f in listdir(directory) if f.endswith(extension))
    return [ join(directory, filename) for filename in files ]

def read_csv(filename):
    print()
    print('Trying to read file "{}"'.format(filename))
    with codecs.open(filename, 'r', ENCODING) as f:
        header = extract_first_line(f)
        lines = [ split(line) for line in f ]
    print('Read {} lines'.format( bool(header) + len(lines) ))
    return header, lines

def extract_first_line(f):
    header = next(f,None)
    return split(header) if header else [ ]

def split(line):
    return line.rstrip('\r\n').split(SEP)    

def get_col_types(header):
    if len(header)==0:
        print('Missing header!')
        return
    col_types = [ TO_TYPE.get(col[-1], None) for col in header ]
    for i, typ in enumerate(col_types):
        if typ is None:
            print('Unrecognized type in column {}: "{}"'.format(i+1, header[i]))
            return
    assert len(col_types)==len(header)
    return col_types

def convert(col_types, lines):
    type_errors, table = [ ], [ ]
    for i, line in enumerate(lines):
        row = [ ]
        for j, col in enumerate(line):
            try:
                row.append( col_types[j](col) )
            except:
                row.append( None )
                type_errors.append((i,j))
        assert len(row)==len(col_types)
        table.append(row)
    if type_errors:
        print('There were type conversion errors!')
        table = None
    return type_errors, table

def write_cell_errors(filename, header, lines, cells_to_mark):
    for cell in cells_to_mark:
        print(cell)
    return

if __name__ == '__main__':
    main()
