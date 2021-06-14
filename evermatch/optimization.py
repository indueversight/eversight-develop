"""
Module that builds the optimization model.

Created by Aster Santana (Jul 14, 20), Opex Analytics.
"""

from evermatch.opt_model_pulp import OptModel


def build_optimization_model(opt_input_dat, params):
    # Build base optimization model
    opt_model = OptModel(opt_input_dat)
    opt_model.build_base_model()
    # Add complexities
    if params['Request Coverage'] == 'Flexible with alternative options':
        opt_model.add_complexity_alternative_assignments()
    if params['Requirement Satisfaction'] == 'Relax scored requirements':
        opt_model.add_complexity_relax_scored_requirement()
    return opt_model
