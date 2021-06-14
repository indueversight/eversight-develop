"""
Action to clean data.

Created by Aster Santana (Apr 25, 2021), Coupa Software.

"""

from evermatch.schemas import input_schema

from evermatch import constants


def automated_data_cleaning_solve(dat):
    assert input_schema.good_pan_dat_object(dat)
    parameters_dict = input_schema.create_full_parameters_dict(dat)
    rtn = input_schema.copy_pan_dat(dat)
    if parameters_dict['Automated Data Cleaning'] == "None":
        pass
    elif parameters_dict['Automated Data Cleaning'] == "Weak":
        input_schema.remove_foreign_key_failures(rtn)
    elif parameters_dict['Automated Data Cleaning'] == "Strong":
        input_schema.remove_foreign_key_failures(rtn)
        input_schema.replace_data_type_failures(rtn)
    else:
        raise NotImplementedError("Please set 'Automated Data Cleaning' to either 'None', 'Weak', or 'Strong'.")
    return {"dat": rtn}


if __name__ == "__main__":
    _dat = input_schema.csv.create_pan_dat(constants.input_path)
    output = automated_data_cleaning_solve(_dat)
    input_schema.csv.write_directory(output["dat"], constants.input_path)
