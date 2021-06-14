"""
This is a placeholder action that needs to be configured depending on how the client data is available.

Reads raw_mar29_apr3 input data from the client data source and maps it to the app input schema.

Created by Aster Santana (Apr 25, 2021), Coupa Software.
"""

from evermatch import constants
from evermatch.schemas import input_schema
from evermatch.data_maintemance import data_check

import pandas as pd


def request_data(dat, requests):
    df = requests.copy()
    df = df.rename(columns={'RequestNumber': 'Request ID',
                            'TissueUse': 'Tissue Use',
                            'SurgeonID': 'Surgeon ID',
                            'LocationID': 'Site ID',
                            'SrgPref_AgeMin': 'Age Min',
                            'SrgPref_AgeMax': 'Age Max',
                            'SrgPref_CellCountMin': 'Cell Count Min',
                            'SrgPref_DeathToPreservationMax': 'Death to Recovery Max (hrs.)',
                            'SrgPref_DeathToSurgeryMax': 'Death to Surgery Max (days)',
                            'SrgPref_DeathToCooling': 'Death to Cooling Max (hrs.)',
                            'SrgPref_ClearZone': 'Clear Zone Min',
                            'ExcludeCancer': 'Exclude Cancer',
                            'ExcludeDiabetes': 'Exclude Diabetes',
                            'ExcludeLASIKScars': 'Exclude LASIK Scars',
                            'ExcludeMatedSets': 'Exclude Mated Set',
                            'ExcludeModerateFolds': 'Exclude Moderate Folds',
                            'ExcludePseudophakicAphakicLens': 'Exclude Artificial Lens',
                            'ExcludeTissueReturned': 'Exclude Tissue Returned'})

    dat.requests = df[[
        'Request ID',
        'Site ID', 'Surgeon ID', 'Exclude Tissue Returned',
        'Tissue Use', 'Age Min', 'Age Max', 'Cell Count Min', 'Death to Recovery Max (hrs.)',
        'Death to Surgery Max (days)', 'Death to Cooling Max (hrs.)', 'Clear Zone Min', 'Exclude Cancer',
        'Exclude Diabetes', 'Exclude LASIK Scars', 'Exclude Mated Set', 'Exclude Moderate Folds',
        'Exclude Artificial Lens']]

    return dat


def tissue_data(dat, tissues):
    df = tissues.copy()
    df = df.rename(columns={'TissueNumber': 'Tissue ID',
                            'TissueLocationID': 'Current Site ID',
                            'DeathToRecovery_Hrs': 'Death to Recovery (hrs.)',
                            'DeathToToday_Days': 'Death to Surgery (days)',
                            'DeathToCoolingHours': 'Death to Cooling (hrs.)',
                            'DonorAge': 'Donor Age',
                            'CellCount': 'Cell Count',
                            'HistoryOfCancer': 'Cancer',
                            'PseudophakicAphakicLens': 'Artificial Lens',
                            'ModerateFolds': 'Moderate Folds',
                            'LASIKScar': 'LASIK Scar',
                            'ClearZone': 'Clear Zone'
                            })

    dat.tissues = df[['Tissue ID',
                      'Current Site ID', 'Returned',
                      'Death to Recovery (hrs.)', 'Death to Surgery (days)', 'Death to Cooling (hrs.)', 'Donor Age',
                      'Cell Count', 'PK', 'DSAEK', 'DMEK', 'Diabetes', 'Cancer', 'Artificial Lens',
                      'Moderate Folds', 'LASIK Scar', 'Clear Zone']]
    return dat


def location_data(dat, locations):
    df = locations.copy()
    df = df.rename(columns={'LocationID': 'Site ID',
                            'Location': 'Hospital'})

    dat.locations = df[['Site ID', 'Hospital']]
    return dat


def surgeon_data(dat, surgeons):
    df = surgeons.copy()
    df = df.rename(columns={'SurgeonID': 'Surgeon ID',
                            'Surgeon': 'Name'})

    dat.surgeons = df[['Surgeon ID', 'Name']]
    return dat


def cost_matrix(dat, cost_matrix1):
    df = cost_matrix1.copy()

    dat.cost_matrix = df[['Origin Site ID',
                          'Dest. Site ID',
                          'Transp. Cost']]
    return dat


def surgeons_pref(dat, surgeons_pref1):
    df = surgeons_pref1.copy()

    dat.surgeons_pref = df[['Surgeon ID',
                            'Cell Count Min',
                            'Age Range',
                            'Death to Recovery Max (hrs.)',
                            'Death to Surgery Max (days)',
                            'Death to Cooling Max (hrs.)',
                            'Tissue Origin']]
    return dat


def data_ingestion_solve(request_df, tissue_df, location_df, surgeon_df, cost_matrix_df, surgeons_pref_df):
    """
    Maps raw_mar29_apr3 data to app data.
    :param request_df: request input raw data.
    :param tissue_df: request input raw data.
    :param location_df: request input raw data.
    :param surgeon_df: request input raw data.
    :param cost_matrix_df: request input raw data.
    :param surgeons_pref_df: request input raw data.
    :return: a good ticdat for the input_schema, or None
    """

    print('#businesslog Executing Data Ingestion Action:')

    dat = input_schema.PanDat()
    dat = request_data(dat, request_df)
    dat = tissue_data(dat, tissue_df)
    dat = location_data(dat, location_df)
    dat = surgeon_data(dat, surgeon_df)
    dat = cost_matrix(dat, cost_matrix_df)
    dat = surgeons_pref(dat, surgeons_pref_df)

    data_check(dat, input_schema)
    print('#businesslog App layers populated successfully')
    return {"dat": dat}


if __name__ == "__main__":

    request_ = pd.read_csv(constants.raw_input_path/'requests.csv')
    tissue_ = pd.read_csv(constants.raw_input_path / 'tissues.csv')
    location_ = pd.read_csv(constants.raw_input_path/'locations.csv')
    surgeon_ = pd.read_csv(constants.raw_input_path / 'surgeons.csv')
    cost_matrix_ = pd.read_csv(constants.raw_input_path / 'cost_matrix.csv')
    surgeons_pref_ = pd.read_csv(constants.raw_input_path / 'surgeons_pref.csv')
    # parameter_ = pd.read_csv(constants.raw_input_path / 'parameters.csv')

    output = data_ingestion_solve(request_, tissue_, location_, surgeon_, cost_matrix_, surgeons_pref_)["dat"]
    print('#businesslog Writing data to the data base')
    input_schema.csv.write_directory(output, constants.raw_input_path)

