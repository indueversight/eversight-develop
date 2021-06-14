"""
Action to clean data.

Created by Aster Santana (Apr 25, 2021), Coupa Software.

"""

from evermatch.schemas import input_schema
from evermatch.schemas import output_schema
from evermatch import constants

from time import time
import warnings


def data_check(dat, schema):
    print('#businesslog Running data integrity checks...')
    starting_time = time()
    assert schema.good_pan_dat_object(dat), 'Not a good PanDat object'
    data_type_failures = schema.find_data_type_failures(dat)
    if data_type_failures:
        print(f'#businesslog Data type failures has been found. See some of them printed in the log.')
        for key, df in data_type_failures.items():
            print(key)
            print(df.head().to_string())
        warnings.warn(f'{len(data_type_failures)} data type failures has been found.')
    data_row_failures = schema.find_data_row_failures(dat)
    if data_row_failures:
        print(f'#businesslog Data row failures has been found. See some of them printed in the log.')
        for key, df in data_row_failures.items():
            print(key)
            print(df.head().to_string())
        warnings.warn(f'{len(data_row_failures)} data row failures has been found.')
    foreign_key_failures = schema.find_foreign_key_failures(dat)
    if foreign_key_failures:
        print(f'#businesslog Foreign key failures has been found. See some of them printed in the log.')
        for key, df in foreign_key_failures.items():
            print(key)
            print(df.head().to_string)
        warnings.warn(f'{len(foreign_key_failures)} foreign key failures has been found.')
    print(f'#businesslog Data check execution time: {round(time() - starting_time)} seconds')


def remove_inactive_records(dat, overwrite_in_directory=False):
    if input_schema.find_foreign_key_failures(dat):
        print("#businesslog Foreign key failures found after removing inactive records from some of the tables: "
              "'materials', 'assets', 'initial_assignment', 'asset_material'")
        print("#businesslog Removing foreign key failures...")
        input_schema.remove_foreign_key_failures(dat)
        if overwrite_in_directory is True:
            input_schema.csv.write_directory(dat, constants.input_path)
