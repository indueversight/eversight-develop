"""
Optimization model for Production Planning and Scheduling (PPS).

Created by Aster Santana (Jun 15, 20), Opex Analytics.

This module has one class, OptModel, which defines the optimization model.
"""
from evermatch.constants import output_path
from evermatch.schemas import input_schema

import pulp
import ticdat
from evermatch.utils import timeit
import numpy as np


class OptModel:
    """Class to define and solve the optimization model."""

    def __init__(self, dat, name="EverMatch"):
        self.dat = dat
        self.params = input_schema.create_full_parameters_dict(dat.dat)
        self.name = name
        self.model = None
        self.vars = dict()
        self.kpi = dict()
        self.obj_function = 0.0
        self.model_sln = dict()
        self.complexities = list()
        self.xx_keys = ticdat.Slicer(dat.x_keys)

    @timeit
    def build_base_model(self):
        self.model = pulp.LpProblem(self.name, sense=pulp.LpMinimize)
        self._add_decision_variables()
        self._add_constraints()
        self._add_objective()
        print("#businesslog Base optimization model built successfully")

    def _add_decision_variables(self):
        print("#businesslog Adding decision variables...")
        # Binary
        x = pulp.LpVariable.dicts(indexs=self.dat.x_keys, cat=pulp.LpBinary, name='x')  # Assignment
        self.vars = {'x': x}

    def _add_constraints(self):
        print("#businesslog Adding constraints...")
        dat, m = self.dat, self.model
        xx_keys = self.xx_keys
        x = self.vars['x']

        # Each tissue_df can be assigned to at most one tissue_df request_df
        for i in dat.I:
            m.addConstraint(pulp.lpSum(x[key] for key in xx_keys.slice(i, '*')) <= 1, name=f't_{i}')

        # Each request_df must be assigned to exactly one tissue_df
        if self.params['Request Coverage'] == 'Exactly one tissue_df per request_df':
            for j in dat.J:
                m.addConstraint(pulp.lpSum(x[key] for key in xx_keys.slice('*', j)) == 1, name=f'r_{j}')

    def _add_objective(self):
        print("#businesslog Adding objective function...")
        dat, m = self.dat, self.model
        x = self.vars['x']
        transportation_cost = pulp.lpSum(dat.tc[key] * x[key] for key in dat.x_keys)
        self.kpi.update({'Transportation Cost': transportation_cost})
        self.obj_function += transportation_cost

    def add_complexity_alternative_assignments(self):
        dat, m = self.dat, self.model
        xx_keys = self.xx_keys
        x = self.vars['x']
        # Add assignment shortfall variables
        y = pulp.LpVariable.dicts(indexs=self.dat.J, cat=pulp.LpContinuous, lowBound=0, upBound=dat.N, name='y')
        self.vars['y'] = y
        # Add soft constraints for tissue_df request_df
        for j in dat.J:
            m.addConstraint(pulp.lpSum(x[key] for key in xx_keys.slice('*', j)) == dat.N - y[j], name=f'r_{j}')
        # Add assignment short fall penalty to the objective
        assignment_shortfall_penalty = pulp.lpSum(dat.p * y[j] for j in dat.J)
        self.kpi.update({'Assignment Shortfall Penalty': assignment_shortfall_penalty})
        self.obj_function += assignment_shortfall_penalty

    def add_complexity_relax_scored_requirement(self):
        dat = self.dat
        x = self.vars['x']
        self.obj_function += -pulp.lpSum(dat.q[key] * x[key] for key in dat.x_keys)

    @timeit
    def optimize(self):
        self.model.setObjective(self.obj_function)
        if self.dat.params['Write lp File'] not in ['None', 'none']:
            self.model.writeLP(self.dat.params['Write lp File'])
        print("#businesslog Solving the optimization model...")
        solver = pulp.PULP_CBC_CMD(msg=True)
        sol = self.model.solve(solver)
        vars_sln = dict()
        self.model_sln = None
        status = pulp.LpStatus[self.model.status]
        print('#businesslog Optimization status: {}'.format(status))
        if sol is not None:
            obj_val = pulp.value(self.model.objective)
            best_bound = np.nan  # sol.solve_details.best_bound
            mip_gap = np.nan  # sol.solve_details.mip_relative_gap
            solve_time = self.model.solutionTime
            kpis = {kpi_name: (kpi if isinstance(kpi, (float, int)) else pulp.value(kpi))
                    for kpi_name, kpi in self.kpi.items()}
            for var_name, var in self.vars.items():
                vars_sln[var_name] = {key: v.value() for key, v in var.items()}
            scores = [(i, j, round(self.dat.q[i, j] * round(v.value()), 2)) for (i, j), v in self.vars['x'].items()]
            self.model_sln = {'status': status, 'vars': vars_sln, 'obj_val': obj_val, 'best_bound': best_bound,
                              'mip_gap': mip_gap, 'solve_time': solve_time, 'kpis': kpis, 'scores': scores}



