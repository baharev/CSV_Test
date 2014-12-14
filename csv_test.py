from __future__ import print_function
import codecs
from os import listdir, makedirs
from os.path import basename, isdir, join, splitext
from shutil import rmtree
from xlsxwriter import Workbook

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

errors = { }
passed = [ ]

def main():
    setup_errors_dir()
    for filename in files_to_check():
        etalon = get_content(ETALON_DIR, filename, 'etalon')
        if etalon is None:
            continue
        tocomp = get_content(TOCOMP_DIR, filename, 'test')
        if tocomp is None:
            continue
        mismatch = compare(etalon, tocomp)
        if mismatch:
            errors[filename] = 'mismatch, excel sheet written'
            write_mismatch(filename, etalon, tocomp, mismatch)
        else:
            passed.append(filename)
    show_summary()

def setup_errors_dir():
    if isdir(ERRORS_DIR):
        rmtree(ERRORS_DIR)
    makedirs(ERRORS_DIR)

def files_to_check():
    etalons = { f for f in listdir(ETALON_DIR) if f.endswith(EXTENSION) }
    tocomps = { f for f in listdir(TOCOMP_DIR) if f.endswith(EXTENSION) }
    etalon_only = etalons - tocomps
    tocomp_only = tocomps - etalons
    for e in etalon_only:
        errors[e] = 'only etalon found'
    for t in tocomp_only:
        errors[t] = 'missing etalon'
    return sorted(etalons & tocomps)

def get_content(directory, filename, kind):
    header, lines = read_csv(join(directory,filename))
    col_types, error_msg = get_col_types(header)
    if error_msg:
        errors[filename] = '{}, header: {}'.format(kind, error_msg)
        return
    # FIXME check row length == header length!
    type_errors, table = convert(col_types, lines)
    if type_errors:
        msg = '{}, type conversion error, excel sheet written'.format(kind)
        errors[filename] = msg
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
    header = next(f,None)
    return split(header) if header else [ ]

def split(line):
    return line.rstrip('\r\n').split(SEP)

def get_col_types(header):
    if len(header)==0:
        return None, 'missing'
    col_types = [ TO_TYPE.get(col[-1], None) for col in header ]
    for i, typ in enumerate(col_types):
        if typ is None:
            msg = 'unrecognized type in column {}: "{}"'.format(i+1, header[i])
            return None, msg
    assert len(col_types)==len(header)
    return col_types, None

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
        table = None
    return type_errors, table

def get_filebase(path):
    return splitext(basename(path))[0]

def write_cell_errors(xlsxname, header, lines, cells_to_mark):
    workbook  = Workbook(join(ERRORS_DIR, xlsxname))
    cell_fmt  = workbook.add_format()
    worksheet = workbook.add_worksheet()
    cell_fmt.set_bg_color('cyan')
    formatter = { cell : cell_fmt for cell in cells_to_mark }
    worksheet.write_row(0, 0, header)
    for i, line in enumerate(lines):
        for j, item in enumerate(line):
            worksheet.write(i+1, j, item, formatter.get((i,j), None))
    workbook.close()

def compare(etalon, tocomp):
    pass

def write_mismatch(filename, etalon, tocomp, mismatch):
    pass

def show_summary():
    print('-------------------------------------------------------------------')
    if passed:
        print('Passed: {} tests'.format(len(passed)))
    if errors:
        msgs = sorted( errors.iteritems() )
        print('There were errors:')
        for fname, msg in msgs:
            print('  {}: {}'.format(fname,msg))
        print('Tests FAILED!')
    else:
        print('Tests PASSED!')

if __name__ == '__main__':
    main()
