"""
Module that contains the main solve.

Created by Aster Santana (May 26, 20), Opex Analytics.

The solve function performs the following steps:
- Prepares the input data for the optimization
- Build de optimization model
- Optimize
- Process the solution
- Populates the output schema
"""

import evermatch.data_maintemance as data_maintenance
import evermatch.optimization as optimization
from evermatch.schemas import input_schema, output_schema
from evermatch.opt_data import OptInputData, OptOutputData
from evermatch import constants


def solve(dat):
    """
    Maps input data to the input optimization data, builds and solves the optimization model, and maps the solution
    to the output data.
    :param dat: A good TicDat for the input schema.
    :return: A good TicDat for the output schema, or None.
    """

    data_maintenance.data_check(dat, input_schema)
    data_maintenance.remove_inactive_records(dat)
    params = input_schema.create_full_parameters_dict(dat)

    opt_input_dat = OptInputData(dat)
    opt_model = optimization.build_optimization_model(opt_input_dat, params)
    opt_model.optimize()
    opt_output_dat = OptOutputData(opt_model.model_sln, params)
    opt_output_dat.populate_output_schema(dat)
    rtn = opt_output_dat.sln

    data_maintenance.data_check(rtn, output_schema)
    return rtn


if __name__ == "__main__":
    _dat = input_schema.csv.create_pan_dat(constants.input_path)
    sln = solve(_dat)
    print('#businesslog Writing data to the data base')
    output_schema.csv.write_directory(sln, constants.output_path)
