"""
Module that contains some constants that are used throughout the package.

Executing locally:
To execute the code solve or any of its action locally, just assign the name of a raw_mar29_apr3 input data from the
../test_[package_name]/data/ directory to the raw_input_data variable below.
Always need to execute action_local_data_ingestion.py fist to populate the ../test_[package_name]/data/inputs/ folder,
from which the other actions and solve code will read/modify the input data.

Created by Aster Santana (Apr 25, 2021), Coupa Software.

"""

from pathlib import Path

package_name = 'evermatch'
data_id = 3
raw_input_data = {1: 'raw_mar29_apr3', 2: 'raw_test', 3: 'raw_data'}[data_id]

# Paths to execute the package locally
raw_input_path = Path.cwd().parent / f"test_{package_name}/data/" / raw_input_data  # Used only by Data Ingestion Action
input_path = Path.cwd().parent / f"test_{package_name}/data/inputs"
output_path = Path.cwd().parent / f"test_{package_name}/data/outputs"

