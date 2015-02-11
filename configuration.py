# Copyright (C) 2014, 2015 by Ali Baharev <ali.baharev@gmail.com>
# All rights reserved.
# BSD license.
# https://github.com/baharev/CSV_Test

# The directory with the expected output (etalon CSV files).
ETALON_DIR = '/home/ali/sg2ps_tests/etalon'
#ETALON_DIR = '/home/ali/sg2ps_tests/empty'

# The directory with the CSV files that should be compared to the etalon CSVs.
#TOCOMP_DIR = '/home/ali/sg2ps_tests/etalon'
#TOCOMP_DIR = '/home/ali/sg2ps_tests/to_compare'
TOCOMP_DIR = '/tmp/sg2ps_tests/to_compare'

# Extension of the input CSV files (both the etalon and the test files). All 
# other file types will be ignored in the comparison.
EXTENSION  = '.csv'

# Separator in the input CSV files.
SEP  = ','

# The spreadsheets show where the errors were detected.
# Careful: all .xlsx files and the log file will be deleted on startup!
SPREADSHEETS_DIR = '/tmp/sg2ps_tests/result'
LOGFILE = 'log.txt'

# The last character of the column name encodes the type. Here we map that 
# charater to a type.
TO_TYPE = { 's' : str,
            'i' : int,
            'd' : float } # NaN should be represented by the string NaN

# Thresholds in floating point comparison
REL_TOL = 1.0e-5
ABS_TOL = 1.0e-5
