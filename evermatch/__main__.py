from ticdat import standard_main

from evermatch.schemas import input_schema, output_schema
from evermatch.solve_code import solve

if __name__ == "__main__":
    standard_main(input_schema, output_schema, solve)
