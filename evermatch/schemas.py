"""
The module that
- Defines TicDat input and output schemas
- Defines user parameters
- Set predicates to inputs and output schemas

Created by Aster Santana (Apr 25, 2021), Coupa Software.

"""

from ticdat import PanDatFactory
import pandas as pd

# region DEFINE SCHEMAS
# region INPUT SCHEMAS
input_schema = PanDatFactory(
    parameters=[['Parameter'], ['Value']],

    locations=[['Site ID'], ['Hospital']],
    surgeons=[['Surgeon ID'], ['Name']],

    cost_matrix=[['Origin Site ID', 'Dest. Site ID'], ['Transp. Cost']],
    tissues=[['Tissue ID'], [
        'Current Site ID', 'Returned',
        'Death to Recovery (hrs.)', 'Death to Surgery (days)', 'Death to Cooling (hrs.)', 'Donor Age',
        'Cell Count', 'PK', 'DSAEK', 'DMEK', 'Diabetes', 'Cancer', 'Artificial Lens',
        'Moderate Folds', 'LASIK Scar', 'Clear Zone']],
    requests=[['Request ID'], [
        'Site ID', 'Surgeon ID', 'Exclude Tissue Returned',
        'Tissue Use', 'Age Min', 'Age Max', 'Cell Count Min', 'Death to Recovery Max (hrs.)',
        'Death to Surgery Max (days)', 'Death to Cooling Max (hrs.)', 'Clear Zone Min', 'Exclude Cancer',
        'Exclude Diabetes', 'Exclude LASIK Scars', 'Exclude Mated Set', 'Exclude Moderate Folds',
        'Exclude Artificial Lens']],
    surgeons_pref=[['Surgeon ID', 'Tissue Use'], [
        'Cell Count Min', 'Age Range', 'Death to Recovery Max (hrs.)', 'Death to Surgery Max (days)',
        'Death to Cooling Max (hrs.)', 'Tissue Origin']]
    )
# endregion

# region OUTPUT SCHEMAS
output_schema = PanDatFactory(
    rpt_matching=[['Request ID'], [
        'Tissue ID', 'Transp. Cost', 'Score',
        'Tissue ID - Alt. 1', 'Transp. Cost - Alt. 1', 'Score - Alt. 1',
        'Tissue ID - Alt. 2', 'Transp. Cost - Alt. 2', 'Score - Alt. 2', 'Penalty']],
    )
# endregion
# endregion


# region DEFINE USER PARAMETERS
# Model Complexities Group
input_schema.add_parameter(name='Automated Data Cleaning', default_value='None', number_allowed=False,
                           strings_allowed=["None", "Weak", "Strong"])
input_schema.add_parameter(name='Time Limit (sec.)', default_value=12 * 60**2, number_allowed=True, must_be_int=True,
                           min=0, max=20*60**2, inclusive_min=True, inclusive_max=True)
input_schema.add_parameter(name='MIP Gap', default_value=0.01, number_allowed=True, must_be_int=False,
                           min=0, max=1, inclusive_min=True, inclusive_max=True)
input_schema.add_parameter(name='Write lp File', default_value='None', number_allowed=False, strings_allowed="*")
input_schema.add_parameter(name='Request Coverage', default_value='Flexible with alternative options',
                           number_allowed=False,
                           strings_allowed=['Exactly one tissue_df per request_df',
                                            'Flexible with alternative options'])
input_schema.add_parameter(name='Num. of Assignments', default_value='Up to three tissues per request_df',
                           strings_allowed=['Up to one tissue_df per request_df',
                                            'Up to two tissues per request_df',
                                            'Up to three tissues per request_df'])
input_schema.add_parameter(name='Assignment Shortfall Penalty', default_value=100, number_allowed=True,
                           min=0, max=1000, inclusive_min=True, inclusive_max=True)
input_schema.add_parameter(name='Requirement Satisfaction', default_value='Relax scored requirements',
                           number_allowed=False,
                           strings_allowed=['Must meet all requirements', 'Relax scored requirements'])
input_schema.add_parameter(name='Cell Count Max Violation', default_value='10%', number_allowed=False,
                           strings_allowed=['0%', '5%', '10%', '20%', '30%'])
input_schema.add_parameter(name='Age Range Max Violation', default_value='0%', number_allowed=False,
                           strings_allowed=['0%', '5%', '10%', '20%', '30%'])
input_schema.add_parameter(name='Death to Recovery Max Violation', default_value='0%', number_allowed=False,
                           strings_allowed=['0%', '5%', '10%', '20%', '30%'])
input_schema.add_parameter(name='Death to Surgery Max Violation', default_value='0%', number_allowed=False,
                           strings_allowed=['0%', '5%', '10%', '20%', '30%'])
input_schema.add_parameter(name='Death to Cooling Max Violation', default_value='0%', number_allowed=False,
                           strings_allowed=['0%', '5%', '10%', '20%', '30%'])
input_schema.add_parameter(name='Reward Type', default_value='Dynamic Reward', number_allowed=False,
                           strings_allowed=['Fixed Reward', 'Dynamic Reward'])
# endregion


# region APPLY DATA TYPES AND PREDICATES TO THE INPUT SCHEMAS

# region locations
table_name = "locations"
text_fields = ['Site ID', 'Hospital']

for col in text_fields:
    input_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*")
# endregion

# region surgeons
table_name = "surgeons"
text_fields = ['Surgeon ID', 'Name']

for col in text_fields:
    input_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*")
# endregion

# region cost_matrix
table_name = "cost_matrix"
text_fields = ['Origin Site ID', 'Dest. Site ID']

input_schema.set_data_type(table_name, 'Transp. Cost', must_be_int=False, min=0, max=float('inf'),
                           inclusive_min=True, inclusive_max=False)
for col in text_fields:
    input_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*")
input_schema.add_foreign_key(table_name, 'locations', [('Origin Site ID', 'Site ID')])
input_schema.add_foreign_key(table_name, 'locations', [('Dest. Site ID', 'Site ID')])
# endregion

# region tissues
table_name = "tissues"
text_fields = ['Tissue ID', 'Current Site ID']
flag_fields = ['PK', 'DSAEK', 'DMEK', 'Diabetes', 'Cancer', 'Artificial Lens', 'Moderate Folds',
               'LASIK Scar', 'Returned']
input_schema.set_data_type(table_name, 'Death to Recovery (hrs.)', must_be_int=False, min=0, max=100,
                           inclusive_min=False, inclusive_max=True)
input_schema.set_data_type(table_name, 'Death to Surgery (days)', must_be_int=False, min=0, max=100,
                           inclusive_min=False, inclusive_max=True)
input_schema.set_data_type(table_name, 'Death to Cooling (hrs.)', must_be_int=False, min=0, max=100,
                           inclusive_min=False, inclusive_max=True)
input_schema.set_data_type(table_name, 'Donor Age', must_be_int=True, min=0, max=120,
                           inclusive_min=False, inclusive_max=True)
input_schema.set_data_type(table_name, 'Cell Count', must_be_int=True, min=0, max=float('inf'),
                           inclusive_min=False, inclusive_max=False)
input_schema.set_data_type(table_name, 'Clear Zone', must_be_int=False, min=0, max=50,
                           inclusive_min=True, inclusive_max=False)
for col in text_fields:
    input_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*")
for col in flag_fields:
    input_schema.set_data_type(table_name, col, must_be_int=True, min=0, max=1, inclusive_min=True, inclusive_max=True)
input_schema.add_foreign_key(table_name, 'locations', [('Current Site ID', 'Site ID')])
# endregion

# region requests
table_name = "requests"
text_fields = ['Site ID', 'Surgeon ID']
flag_fields = ['Exclude Tissue Returned', 'Exclude Cancer', 'Exclude Diabetes', 'Exclude LASIK Scars',
               'Exclude Mated Set', 'Exclude Moderate Folds', 'Exclude Artificial Lens']
input_schema.set_data_type(table_name, 'Tissue Use', strings_allowed=['PK', 'DSAEK', 'DMEK'])
input_schema.set_data_type(table_name, 'Age Min', must_be_int=True, min=0, max=120,
                           inclusive_min=True, inclusive_max=True)
input_schema.set_data_type(table_name, 'Age Max', must_be_int=True, min=0, max=120,
                           inclusive_min=True, inclusive_max=True)
input_schema.set_data_type(table_name, 'Cell Count Min', must_be_int=True, min=0, max=float('inf'),
                           inclusive_min=True, inclusive_max=False)
input_schema.set_data_type(table_name, 'Death to Recovery Max (hrs.)', must_be_int=False, min=0, max=100,
                           inclusive_min=True, inclusive_max=True)
input_schema.set_data_type(table_name, 'Death to Surgery Max (days)', must_be_int=False, min=0, max=100,
                           inclusive_min=True, inclusive_max=True)
input_schema.set_data_type(table_name, 'Death to Cooling Max (hrs.)', must_be_int=False, min=0, max=100,
                           inclusive_min=True, inclusive_max=True)
input_schema.set_data_type(table_name, 'Clear Zone Min', must_be_int=False, min=0, max=50,
                           inclusive_min=True, inclusive_max=False)
for col in text_fields:
    input_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*")
for col in flag_fields:
    input_schema.set_data_type(table_name, col, must_be_int=True, min=0, max=1, inclusive_min=True, inclusive_max=True)
input_schema.add_foreign_key(table_name, 'surgeons', [('Surgeon ID', 'Surgeon ID')])
input_schema.add_foreign_key(table_name, 'locations', [('Site ID', 'Site ID')])
input_schema.add_data_row_predicate(table_name, predicate_name="Age Min <= Age Max",
                                    predicate=lambda row: row['Age Min'] <= row['Age Max'])
# endregion

# region surgeons_pref
table_name = "surgeons_pref"
text_fields = ['Surgeon ID']
score_fields = ['Cell Count Min', 'Age Range', 'Death to Recovery Max (hrs.)', 'Death to Surgery Max (days)',
                'Death to Cooling Max (hrs.)', 'Tissue Origin']
input_schema.set_data_type(table_name, 'Tissue Use', strings_allowed=['PK', 'DSAEK', 'DMEK'])
for col in text_fields:
    input_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*")
for col in score_fields:
    input_schema.set_data_type(table_name, col, must_be_int=False, min=0, max=1, inclusive_min=True, inclusive_max=True)
input_schema.add_foreign_key(table_name, 'surgeons', [('Surgeon ID', 'Surgeon ID')])
input_schema.add_data_row_predicate(table_name, predicate_name="Scores add up to 1.0",
                                    predicate=lambda row: abs(sum(row[col_] for col_ in score_fields) - 1) < 1e-4)
# endregion
# endregion


# region APPLY DATA TYPES AND PREDICATES TO THE OUTPUT SCHEMA

# region rpt_matching
table_name = "rpt_matching"
nullable_text_fields = ['Tissue ID', 'Tissue ID - Alt. 1', 'Tissue ID - Alt. 2']
nullable_float_field = ['Transp. Cost', 'Transp. Cost - Alt. 1', 'Transp. Cost - Alt. 2', 'Penalty']
output_schema.set_data_type(table_name, 'Request ID', number_allowed=False, strings_allowed="*")
for col in nullable_text_fields:
    output_schema.set_data_type(table_name, col, number_allowed=False, strings_allowed="*", nullable=True)
for col in nullable_float_field:
    output_schema.set_data_type(table_name, col, must_be_int=False, min=0, max=float('inf'),
                                inclusive_min=True, inclusive_max=False, nullable=True)
for col in ['Score', 'Score - Alt. 1', 'Score - Alt. 2']:
    output_schema.set_data_type(table_name, col, must_be_int=False, min=-float('inf'), max=float('inf'),
                                inclusive_min=False, inclusive_max=False, nullable=True)
# endregion

# endregion
