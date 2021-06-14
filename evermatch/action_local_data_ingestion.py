"""
This is a placeholder action that needs to be configured depending on how the client data is available.

Reads raw_mar29_apr3 input data from the client data source and maps it to the app input schema.

Created by Aster Santana (Apr 25, 2021), Coupa Software.
"""

from evermatch import constants
from evermatch.schemas import input_schema
from evermatch.data_maintemance import data_check


def data_ingestion_solve(dat):
    """
    Maps raw_mar29_apr3 data to app data.
    :param dat: a good ticdat for the input_schema
    :return: a good ticdat for the input_schema, or None
    """

    print('#businesslog Executing Data Ingestion Action:')

    rtn = dat
    data_check(dat, input_schema)
    print('#businesslog App layers populated successfully')
    return {"dat": rtn}


if __name__ == "__main__":
    _dat = input_schema.csv.create_pan_dat(constants.raw_input_path)
    output = data_ingestion_solve(_dat)["dat"]
    print('#businesslog Writing data to the data base')
    input_schema.csv.write_directory(output, constants.input_path)

