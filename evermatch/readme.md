### Package directory


* `schemas.py`<br/>
    - Defines TicDat input and output schema.
    - Defines user parameters.
    - Set predicates (data type, foreign key constraints
      and other integrity checks) to input and 
      output schema.

* `opt_data.py`<br/>
    Has two classes:
    - `OptInputData`: Defines the input optimization 
      data model and maps the input tables (defined 
      by the TicDat input schema) to it.
    - `OptOutputData`: Reads the solution from the 
      optimization and populates the output tables 
      (defined by the TicDat output schema).

* `opt_model.py`<br/>
    Hosts the `OptModel` class, which defines the
    MIP model.

* `optimization.py`<br/>
    Simply builds the optimization model according
    to the user input parameters.
    
* `solve_code.py`<br/>
    The main solve that stitches all together:
    - Prepares the input data for the optimization.
    - Builds de optimization model.
    - Optimizes de model.
    - Processes the solution from the optimization.
    - Populates the output schema.
    
* `__init__`<br/>
    Contains all the configuration for the OpenX app.