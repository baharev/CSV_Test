#!/usr/bin/env python
from __future__ import print_function
import codecs
from itertools import izip, izip_longest
from math import isnan
from os import listdir, makedirs
from os.path import basename, isdir, join, splitext
from shutil import rmtree
from xlsxwriter import Workbook

# The directory with the expected output (etalon CSV files).
ETALON_DIR = '/home/ali/sg2ps_tests/etalon'

# The directory with the CSV files that should be compared to the etalon CSVs.
#TOCOMP_DIR = '/home/ali/sg2ps_tests/etalon'
TOCOMP_DIR = '/home/ali/sg2ps_tests/to_compare'

# Extension of the input CSV files (both the etalon and the test files). All 
# other file types will be ignored in the comparison.
EXTENSION  = '.csv'

# Separator in the input CSV files.
SEP  = ','

# The spreadsheets show where the errors were detected.
# Careful: The contents of this directory will be deleted on startup!
SPREADSHEETS_DIR = '/tmp/sg2ps_tests/result'

# The last character of the column name encodes the type. Here we map that 
# charater to a type.
TO_TYPE = { 's' : str,
            'i' : int,
            'd' : float } # NaN should be represented by the string NaN

# Thresholds in floating point comparison
REL_TOL = 1.0e-5
ABS_TOL = 1.0e-5

#-------------------------------------------------------------------------------
# Normally, there should be no need to modify anything below.

ENCODING = 'ascii'
errors = { }

def main():
    setup_spreadsheets_dir()
    passed = [ fname for fname in files_to_check() if check(fname) ]
    show_summary(passed)

def setup_spreadsheets_dir():
    if isdir(SPREADSHEETS_DIR):
        rmtree(SPREADSHEETS_DIR)
    makedirs(SPREADSHEETS_DIR)

def files_to_check():
    etalons = { f for f in listdir(ETALON_DIR) if f.endswith(EXTENSION) }
    tocomps = { f for f in listdir(TOCOMP_DIR) if f.endswith(EXTENSION) }
    etalon_only = etalons - tocomps
    tocomp_only = tocomps - etalons
    for e in etalon_only:
        log_error(e, 'only etalon found but the test file is missing')
    for t in tocomp_only:
        log_error(t, 'the etalon is missing for this test file')
    return sorted(etalons & tocomps)

def check(filename):
    etalon = get_content(ETALON_DIR, filename, 'etalon')
    if etalon is None:
        return
    tocomp = get_content(TOCOMP_DIR, filename, 'test')
    if tocomp is None:
        return
    mismatch = compare_headers(etalon, tocomp)
    if mismatch:
        log_error(filename, 'mismatch in headers, excel sheet written')
        write_mismatch(filename, etalon, tocomp, mismatch)
        return
    etalon_len, tocomp_len = number_of_rows(etalon, tocomp)
    if etalon_len!=tocomp_len:
        msg = 'number of rows: {}!={}'.format(etalon_len, tocomp_len)
        log_error(filename, msg)
        return
    mismatch = compare_values(etalon, tocomp)
    if mismatch:
        log_error(filename, 'mismatch, excel sheet written')
        write_mismatch(filename, etalon, tocomp, mismatch)
        return
    return True

def log_error(filename, msg):
    assert filename not in errors, filename
    errors[filename] = msg

def get_content(directory, filename, kind):
    header, lines = read_csv( join(directory,filename) )
    col_types, error_msg = get_col_types(header)
    if error_msg:
        log_error(filename, '{}, header: {}'.format(kind, error_msg))
        return
    # FIXME check row length == header length!
    table, type_errors = convert(col_types, lines)
    if type_errors:
        msg = '{}, type conversion errors, excel sheet written'.format(kind)
        log_error(filename, msg)
        xlsxname = get_filebase(filename) + '_'+kind+'_type_error.xlsx'
        write_cell_errors(xlsxname, header, lines, type_errors)
        return
    return header, table

def read_csv(filename):
    print()
    print('Trying to read file "{}"'.format(filename))
    with codecs.open(filename, 'r', ENCODING) as f:
        header = extract_first_line(f)
        lines = [ split(line) for line in f ]
    print('Read {} lines'.format( bool(header) + len(lines) ))
    return header, lines

def extract_first_line(f):
    header = next(f, None)
    return split(header) if header else [ ]

def split(line):
    return line.rstrip('\r\n').split(SEP)

def get_col_types(header):
    # Returns ([type converters], error message). Exactly one of them is None.
    if len(header)==0:
        return None, 'missing'
    col_types = [ TO_TYPE.get(col[-1:], None) for col in header ]
    for i, typ in enumerate(col_types):
        if typ is None:
            msg = 'unrecognized type in column {}: "{}"'.format(i+1, header[i])
            return None, msg
    assert len(col_types)==len(header)
    return col_types, None

def convert(col_types, lines):
    # Returns the tuple of: lines converted to a 2D table with proper types, and
    # the cell indices where type conversion error occured.
    table, type_errors = [ ], [ ]
    for i, line in enumerate(lines,1):
        row = [ ]
        for j, col in enumerate(line):
            try:
                row.append( col_types[j](col) )
            except:
                row.append( None )
                type_errors.append((i,j))
        assert len(row)==len(col_types)
        table.append(row)
    return table if len(type_errors)==0 else [ ], type_errors 

def get_filebase(path):
    return splitext(basename(path))[0]

def write_cell_errors(xlsxname, header, lines, cells_to_mark):
    workbook  = Workbook(join(SPREADSHEETS_DIR, xlsxname))
    cell_fmt  = workbook.add_format()
    cell_fmt.set_bg_color('cyan')
    worksheet = workbook.add_worksheet()
    write_sheet(worksheet, cell_fmt, header, lines, cells_to_mark)
    workbook.close()

def write_mismatch(filename, etalon, tocomp, mismatch):
    workbook  = Workbook(join(SPREADSHEETS_DIR, get_filebase(filename)+'.xlsx'))
    cell_fmt  = workbook.add_format()
    cell_fmt.set_bg_color('cyan')
    worksheet = workbook.add_worksheet(name='test')
    write_sheet(worksheet, cell_fmt, *tocomp, cells_to_mark=mismatch)
    worksheet = workbook.add_worksheet(name='etalon')
    write_sheet(worksheet, cell_fmt, *etalon)
    workbook.close()

def write_sheet(worksheet, cell_fmt, header, lines, cells_to_mark=[]):
    formatter = { cell : cell_fmt for cell in cells_to_mark }
    for j, col_header in enumerate(header):
        worksheet.write(0, j, col_header, formatter.get((0,j), None))
    for i, line in enumerate(lines, 1):
        for j, item in enumerate(line):
            worksheet.write(i,j, replace_nan(item), formatter.get((i,j),None))

def replace_nan(item):
    return 'NaN' if isinstance(item, float) and isnan(item) else item

def compare_headers(etalon, tocomp):
    mismatch = [ ]
    e_head, _ = etalon
    t_head, _ = tocomp
    for i, (eh, th) in enumerate(izip_longest(e_head, t_head, fillvalue='')):
        if eh!=th:
            mismatch.append((0,i))
    return mismatch

def number_of_rows(etalon, tocomp):
    return len(etalon[1]), len(tocomp[1])

def compare_values(etalon, tocomp):
    mismatch = [ ]
    _, e_table = etalon
    _, t_table = tocomp
    for i, (e_row, t_row) in enumerate(izip(e_table, t_table), 1):
        for j, (e_item, t_item) in enumerate(izip(e_row, t_row)):
            if not equals(e_item, t_item):
                mismatch.append((i,j))
    return mismatch

def equals(e, t):
    return compare_floats(e, t) if isinstance(e, float) else e==t 

def compare_floats(e, t):
    e_nan, t_nan = isnan(e), isnan(t)
    if e_nan and t_nan:
        return True
    elif e_nan or t_nan:
        return False
    else:
        assert not e_nan and not t_nan
        diff = abs(e-t)
        return diff < ABS_TOL or diff < REL_TOL*abs(e)

def show_summary(passed):
    print('-------------------------------------------------------------------')
    if passed:
        print('Passed: {} tests'.format(len(passed)))
    if errors:
        msgs = sorted( errors.iteritems() )
        print('There were errors:')
        for fname, msg in msgs:
            print('  {} {}'.format(fname,msg))
        # FIXME write_errors into a log file to the results directory as well!
        #       Write the etalon and test dirs on the top of that log file
        print('Tests FAILED!')
    else:
        print('Tests PASSED!')
    # FIXME Check if etalon and test are the same, warn if yes!

if __name__ == '__main__':
    main()
