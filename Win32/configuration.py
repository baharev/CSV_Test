# Copyright (C) 2014, 2015 by Ali Baharev <ali.baharev@gmail.com>
# All rights reserved.
# BSD license.

from tempfile import gettempdir
from os.path import join, abspath, dirname, normcase, normpath

SG2PS_HOME = normcase(normpath(dirname(dirname(__file__))))

# The directory with the expected output (etalon CSV files).
ETALON_DIR = join(SG2PS_HOME, 'etalon')

# The directory with the CSV files that should be compared to the etalon CSVs.
TOCOMP_DIR = join(gettempdir(), 'sg2ps_tests', 'to_compare')

# Extension of the input CSV files (both the etalon and the test files). All 
# other file types will be ignored in the comparison.
EXTENSION  = '.csv'

# Separator in the input CSV files.
SEP  = '\t'

# The spreadsheets show where the errors were detected.
# Careful: all .xlsx files and the log file will be deleted on startup!
SPREADSHEETS_DIR = join(gettempdir(), 'sg2ps_tests', 'results')
LOGFILE = 'log.txt'

# The last character of the column name encodes the type. Here we map that 
# charater to a type.
TO_TYPE = { 's' : str,
            'i' : int,
            'd' : float } # NaN should be represented by the string NaN

# Thresholds in floating point comparison
REL_TOL = 1.0e-5
ABS_TOL = 1.0e-5
