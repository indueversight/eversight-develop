
from evermatch.schemas import input_schema
from evermatch.schemas import output_schema as solution_schema
from evermatch.solve_code import solve
from evermatch.action_data_cleaning import automated_data_cleaning_solve
from evermatch.action_local_data_ingestion import data_ingestion_solve


__version__ = "1.0.0"
__author__ = """Aster Santana"""
__credits__ = []
__copyright__ = "Coupa Software"
__doc__ = """Eversight Matching Problem"""
__all__ = ["input_schema", "solution_schema", "solve"]


enframe_kwargs = {
    'prepend_usage': 'minimal',
    "advanced_parameters": [  # Will not be displayed in the UI and TicDat will automatically create an
        # Advanced Parameters table in the inputs tab.
        'Write lp File', 'Automated Data Cleaning'],
    'input_display_names': {},
    'solution_display_names': {}
    }


tag_tables_dict = {
    "Master Data": ["locations"],
    "Matching Data": ["tissues", "requests"],
    "Report Data": ["rpt_matching"]
    }

enframe_input_config = {
    "table_ordering": tag_tables_dict["Master Data"] + tag_tables_dict["Matching Data"],
    "table_tags": {k: tag_tables_dict[k] for k in ["Master Data", "Matching Data"]},
    # "invisible_tables": ['raw_table_one', 'raw_table_two'],
    # "invisible_columns": [('table_name', 'column_name')],
    "use_integral_types": True
    }

enframe_output_config = {
    "table_ordering": tag_tables_dict["Report Data"],
    "table_tags": {k: tag_tables_dict[k] for k in ["Report Data"]},
    "use_integral_types": True
    }

params_groups = {
    "Optimization Configuration": ['MIP Gap', 'Time Limit (sec.)']
    }

enframe_parameters_config = {
    "group_name_overrides": params_groups,
    "group_name_sorting": ['Optimization Configuration'],
    "parameter_sorting": params_groups['Optimization Configuration']
    }


enframe_ticdat_actions = {
    "1. Data Ingestion": data_ingestion_solve,
    "2. Automated Cleaning": automated_data_cleaning_solve
    }

# enframe_ticdat_output_actions = {"Email Reports"}
