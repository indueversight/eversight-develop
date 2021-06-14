"""
Optimization data model for Ever Sight matching problem.

Created by Aster Santana (Apr 25, 2021), Coupa Software.

This module has two classes:
OptInputData - Defines the input optimization data model and maps the input tables (defined by the TicDat input schema)
to it.
OptOutputData - Reads the solution from the optimization and populates the output tables (defined by the TicDat output
schema).
"""
import math

import numpy as np

from evermatch.schemas import input_schema
from evermatch.schemas import output_schema
import pandas as pd
import datetime

from evermatch.utils import timeit


class OptInputData:
    """Class to map data from input schema to optimization input schema."""

    def __init__(self, dat):
        """
        Read and process input data (TicDat input schema) to populate the optimization input data.
        :param dat: A good TicDat for the input schema.
        """

        self.dat = dat
        self.params = input_schema.create_full_parameters_dict(dat)

        self.candidate_matches = None

        # SET OF INDICES
        self.I = list()  # materials
        self.J = list()  # assets

        # DATA PARAMETERS
        self.tc = dict()  # transportation cost
        self.r = dict()  # allocated rewards (score for relaxed requirements)
        self.cc = dict()  # tissue_df cell count
        self.ccl = dict()  # request_df minimum cell count
        self.a = dict()  # tissue_df donor age
        self.al = dict()  # request_df donor age min
        self.au = dict()  # request_df donor age max
        self.dr = dict()  # tissue_df death to recover
        self.dru = dict()  # request_df death to recover max
        self.ds = dict()  # tissue_df death to surgery
        self.dsu = dict()  # request_df death to surgery max
        self.dc = dict()  # tissue_df death to cooling
        self.dcu = dict()  # request_df death to cooling max
        self.q = dict()  # scores
        self.N = {'Up to one tissue_df per request_df': 1, 'Up to two tissues per request_df': 2,
                  'Up to three tissues per request_df': 3}[self.params['Num. of Assignments']]
        self.p = self.params['Assignment Shortfall Penalty']

        # VARIABLES KEYS
        self.x_keys = list()  # x[i, j] - keys for matching variables

        self.get_candidate_matches()
        self.populate_set_of_indices()
        self.populate_parameters()
        self.define_variables_keys()
        self.soft_requirement_coefficients()
        self.print_parameters()
        self.print_data_statistics()

    def get_candidate_matches(self):
        dat = self.dat
        tissues_df = dat.tissues.copy()
        requests_df = dat.requests.copy()
        # cross join tissues and requests
        tissues_df['Key'] = 0
        requests_df['Key'] = 0
        df = pd.merge(tissues_df, requests_df, on='Key', how='outer')
        # exclude obvious infeasible combinations
        cell_count_violation = {
            '0%': 0, '5%': 0.05, '10%': 0.1, '20%': 0.2, '30%': 0.3}[self.params['Cell Count Max Violation']]
        age_range_violation = {
            '0%': 0, '5%': 0.05, '10%': 0.1, '20%': 0.2, '30%': 0.3}[self.params['Age Range Max Violation']]
        death_to_recovery_violation = {
            '0%': 0, '5%': 0.05, '10%': 0.1, '20%': 0.2, '30%': 0.3}[self.params['Death to Recovery Max Violation']]
        death_to_surgery_violation = {
            '0%': 0, '5%': 0.05, '10%': 0.1, '20%': 0.2, '30%': 0.3}[self.params['Death to Surgery Max Violation']]
        death_to_cooling_violation = {
            '0%': 0, '5%': 0.05, '10%': 0.1, '20%': 0.2, '30%': 0.3}[self.params['Death to Cooling Max Violation']]
        df = df[
            (df['Donor Age'] >= (1 - age_range_violation) * df['Age Min']) &
            (df['Donor Age'] <= (1 + age_range_violation) * df['Age Max']) &
            (df['Cell Count'] >= (1 - cell_count_violation) * df['Cell Count Min']) &
            (df['Returned'] <= 1 - df['Exclude Tissue Returned']) &
            (
                    (df['PK'] == 1) & (df['Tissue Use'] == 'PK') |
                    (df['DSEAK'] == 1) & (df['Tissue Use'] == 'DSEAK') |
                    (df['DMEK'] == 1) & (df['Tissue Use'] == 'DMEK')
            ) &
            (df['Death to Recovery (hrs.)'] <= (1 + death_to_recovery_violation) * df['Death to Recovery Max (hrs.)']) &
            (df['Death to Surgery (days)'] <= (1 + death_to_surgery_violation) * df['Death to Surgery Max (days)']) &
            (df['Death to Cooling (hrs.)'] <= (1 + death_to_cooling_violation) * df['Death to Cooling Max (hrs.)']) &
            (df['Clear Zone'] >= df['Clear Zone Min']) &
            (df['Cancer'] <= 1 - df['Exclude Cancer']) &
            (df['Diabetes'] <= 1 - df['Exclude Diabetes']) &
            (df['LASIK Scar'] <= 1 - df['Exclude LASIK Scars']) &
            (df['Moderate Folds'] <= 1 - df['Exclude Moderate Folds']) &
            (df['Artificial Lens'] <= 1 - df['Exclude Artificial Lens'])
            ]
        self.candidate_matches = df

    def populate_set_of_indices(self):
        # tissues
        self.I = list(set(self.candidate_matches['Tissue ID']))
        # requests
        self.J = list(set(self.candidate_matches['Request ID']))

    def populate_parameters(self):
        dat = self.dat
        df_cost = self.candidate_matches.merge(
            dat.cost_matrix, left_on=['Current Site ID', 'Site ID'], right_on=['Origin Site ID', 'Dest. Site ID'],
            how='left')
        df_cost['Transp. Cost'] = df_cost['Transp. Cost'].fillna(0.0)
        # transportation cost
        self.tc = dict(zip(zip(df_cost['Tissue ID'], df_cost['Request ID']), df_cost['Transp. Cost']))
        # allocated reward
        srg_pref = dat.requests[['Request ID', 'Surgeon ID', 'Tissue Use']].merge(
            dat.surgeons_pref, on=['Surgeon ID', 'Tissue Use'], how='left')
        srg_pref = srg_pref.fillna(0.0)
        for index, row in srg_pref.iterrows():
            self.r[row['Request ID']] = {col: row[col] for col in [
                'Cell Count Min', 'Age Range', 'Death to Recovery Max (hrs.)', 'Death to Surgery Max (days)',
                'Death to Cooling Max (hrs.)', 'Tissue Origin']}
        # tissue_df cell count
        self.cc = dict(zip(dat.tissues['Tissue ID'], dat.tissues['Cell Count']))
        # request_df cell count minimum
        self.ccl = dict(zip(dat.requests['Request ID'], dat.requests['Cell Count Min']))
        # tissue_df donor age
        self.a = dict(zip(dat.tissues['Tissue ID'], dat.tissues['Donor Age']))
        # request_df donor age min
        self.al = dict(zip(dat.requests['Request ID'], dat.requests['Age Min']))
        # request_df donor age max
        self.au = dict(zip(dat.requests['Request ID'], dat.requests['Age Max']))
        # tissue_df death to recover
        self.dr = dict(zip(dat.tissues['Tissue ID'], dat.tissues['Death to Recovery (hrs.)']))
        # request_df death to recover max
        self.dru = dict(zip(dat.requests['Request ID'], dat.requests['Death to Recovery Max (hrs.)']))
        # tissue_df death to surgery
        self.ds = dict(zip(dat.tissues['Tissue ID'], dat.tissues['Death to Surgery (days)']))
        # request_df death to surgery max
        self.dsu = dict(zip(dat.requests['Request ID'], dat.requests['Death to Surgery Max (days)']))
        # tissue_df death to cooling
        self.dc = dict(zip(dat.tissues['Tissue ID'], dat.tissues['Death to Cooling (hrs.)']))
        # request_df death to cooling max
        self.dcu = dict(zip(dat.requests['Request ID'], dat.requests['Death to Recovery Max (hrs.)']))

    def define_variables_keys(self):
        self.x_keys = list(set(self.candidate_matches[['Tissue ID', 'Request ID']].itertuples(index=False, name=None)))

    def soft_requirement_coefficients(self):
        x_keys = self.x_keys
        for i, j in x_keys:
            r = self.r[j]
            # cell count
            if (self.params['Reward Type'] == 'Fixed Reward') and (self.ccl[j] <= self.cc[i]):
                cq = r['Cell Count Min']
            else:
                cq = r['Cell Count Min'] * (self.cc[i] - self.ccl[j]) / self.ccl[j]
            # age range
            if (self.al[j] <= self.a[i]) and (self.a[i] <= self.au[j]):
                aq = r['Age Range']
            elif self.a[i] < self.al[j]:
                aq = r['Age Range'] * (self.a[i] - self.al[j]) / self.al[j]
            else:  # self.au[j] < self.a[i]
                aq = r['Age Range'] * (self.au[j] - self.a[i]) / self.au[j]
            # death to recovery
            if (self.params['Reward Type'] == 'Fixed Reward') and (self.dr[i] <= self.dru[j]):
                drq = r['Death to Recovery Max (hrs.)']
            else:
                drq = r['Death to Recovery Max (hrs.)'] * (self.dru[j] - self.dr[i]) / self.dru[j]
            # death to surgery
            if (self.params['Reward Type'] == 'Fixed Reward') and (self.ds[i] <= self.dsu[j]):
                dsq = r['Death to Surgery Max (days)']
            else:
                dsq = r['Death to Surgery Max (days)'] * (self.dsu[j] - self.ds[i]) / self.dsu[j]
            # death to cooling
            if (self.params['Reward Type'] == 'Fixed Reward') and (self.dc[i] <= self.dcu[j]):
                dcq = r['Death to Cooling Max (hrs.)']
            else:
                dcq = r['Death to Cooling Max (hrs.)'] * (self.dcu[j] - self.dc[i]) / self.dcu[j]
            self.q[i, j] = cq + aq + drq + dsq + dcq

    def print_parameters(self):
        params_dict = {'Parameter': list(), 'Value': list()}
        for p, v in self.params.items():
            params_dict['Parameter'].append(p)
            params_dict['Value'].append(v)
        params_df = pd.DataFrame(params_dict)
        print('\n', params_df)

    def print_data_statistics(self):
        meta_dict = {
            'Object': ['Tissues', 'Requests'],
            'Stats': [len(self.I), len(self.J)]}
        meta_df = pd.DataFrame(meta_dict)
        print('\n', meta_df, '\n')


class OptOutputData:
    """Class to map data from optimization solution dictionary to output schema (a TicDat output schema)."""

    def __init__(self, model_sln, params):
        self.params = params
        self.model_sln = model_sln
        self.matching_df = None
        self.penalty_df = None
        self.sln = None
        self.process_solution()

    @timeit
    def process_solution(self):
        assert self.model_sln, "Model does not have a solution yet, possibly because it's infeasible (see log above)."
        print('#businesslog Objective Value: {}'.format(self.model_sln['obj_val']))

        sln_vars = self.model_sln['vars']
        # Retrieve production variables
        x_df = pd.Series(sln_vars['x']).reset_index()
        x_df.columns = ['Tissue ID', 'Request ID', 'Value']
        self.matching_df = x_df[['Tissue ID', 'Request ID', 'Value']]

        # Retrieve penalty variables
        y_df = pd.Series(sln_vars['y']).reset_index()
        y_df.columns = ['Request ID', 'Penalty']
        self.penalty_df = y_df[['Request ID', 'Penalty']]

    @timeit
    def populate_output_schema(self, dat):
        sln = output_schema.PanDat()

        # region Populate the rtp_production table
        cols = ['Request ID', 'Tissue ID', 'Transp. Cost', 'Score',
                'Tissue ID - Alt. 1', 'Transp. Cost - Alt. 1', 'Score - Alt. 1',
                'Tissue ID - Alt. 2', 'Transp. Cost - Alt. 2', 'Score - Alt. 2', 'Penalty']
        matching = self.matching_df
        matching = matching[matching['Value'] > 0.5]
        # bring in request_df and tissue_df location
        matching = matching.merge(dat.requests[['Request ID', 'Site ID']], on='Request ID', how='left')
        matching = matching.merge(dat.tissues[['Tissue ID', 'Current Site ID']], on='Tissue ID', how='left')
        matching = matching[['Request ID', 'Tissue ID', 'Current Site ID', 'Site ID', 'Value']].reset_index()
        # get scores
        score_df = pd.DataFrame(self.model_sln['scores'], columns=['Tissue ID', 'Request ID', 'Score'])
        matching = matching.merge(score_df, on=['Request ID', 'Tissue ID'], how='left')
        # get transportation cost
        matching = matching.merge(dat.cost_matrix, how='left',
                                  left_on=['Current Site ID', 'Site ID'], right_on=['Origin Site ID', 'Dest. Site ID'])
        # split assignment into main, alt. 1, and alt. 2
        matching_dict = {col: list() for col in cols[:-1]}
        for request_id, group_df in matching.groupby('Request ID'):
            group_df = group_df[group_df['Value'] > 0.5]
            group_df['Transp. Cost'] = group_df['Transp. Cost'].fillna(0)
            if group_df.empty:
                for col in cols[1:]:
                    matching_dict[col].append(np.nan)
                continue
            group_df = group_df.sort_values(['Transp. Cost', 'Score'], ascending=[True, False]).reset_index()
            matching_dict['Request ID'].append(request_id)
            # main assignment
            try:
                r0 = group_df.iloc[0]
            except IndexError:
                r0 = {'Tissue ID': np.nan, 'Transp. Cost': np.nan, 'Score': np.nan}
            matching_dict['Tissue ID'].append(r0['Tissue ID'])
            matching_dict['Transp. Cost'].append(r0['Transp. Cost'])
            matching_dict['Score'].append(r0['Score'])
            # first alternative assignment
            try:
                r1 = group_df.iloc[1]
            except IndexError:
                r1 = {'Tissue ID': np.nan, 'Transp. Cost': np.nan, 'Score': np.nan}
            matching_dict['Tissue ID - Alt. 1'].append(r1['Tissue ID'])
            matching_dict['Transp. Cost - Alt. 1'].append(r1['Transp. Cost'])
            matching_dict['Score - Alt. 1'].append(r1['Score'])
            # second alternative assignment
            try:
                r2 = group_df.iloc[2]
            except IndexError:
                r2 = {'Tissue ID': np.nan, 'Transp. Cost': np.nan, 'Score': np.nan}
            matching_dict['Tissue ID - Alt. 2'].append(r2['Tissue ID'])
            matching_dict['Transp. Cost - Alt. 2'].append(r2['Transp. Cost'])
            matching_dict['Score - Alt. 2'].append(r2['Score'])
        rpt_matching = pd.DataFrame(matching_dict, columns=cols[:-1])
        # get assignment shortfall penalties
        rpt_matching = rpt_matching.merge(self.penalty_df, on='Request ID', how='left')
        sln.rpt_matching = rpt_matching[cols]
        # endregion

        # region Populate rpt_kpi_summary table
        kpis = [
            ('Objective Value', self.model_sln['obj_val']),
            ('Best Bound', self.model_sln['best_bound'])
        ]
        mip_gap = self.model_sln['mip_gap']
        solve_time = self.model_sln['solve_time']
        kpis += [(kpi_name, kpi) for kpi_name, kpi in self.model_sln['kpis'].items()]
        kpis = [(kpi, math.nan if math.isnan(val) else int(round(val, 0))) for kpi, val in kpis]
        kpis.insert(2, ('MIP Gap (%)', math.nan if math.isnan(mip_gap) else round(100 * mip_gap, 2)))
        kpis.insert(3, ('Solve Time',  math.nan if math.isnan(solve_time) else round(solve_time, 2)))
        kpi_summary = pd.DataFrame(kpis, columns=['KPI', 'Value'])
        sln.rpt_kpi_summary = kpi_summary
        print('\n', kpi_summary, '\n')
        # endregion

        self.sln = sln
