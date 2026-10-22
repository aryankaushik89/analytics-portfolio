"""Targeted checks for the estimate, join grain and decision failure paths."""

from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis import load_sources
from analysis import user_outcomes
from analysis import sql_outcomes
from analysis import data_checks
from analysis import experiment_quality
from analysis import filtered
from analysis import summarize
from analysis import wilson_interval
from analysis import difference_interval
from analysis import sample_ratio
from analysis import select_development_groups
from analysis import economic_result
from analysis import decision
from analysis import planned_sample_size


class ExperimentChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw, cls.events, cls.metadata = load_sources()
        cls.users = user_outcomes(cls.raw, cls.events, cls.metadata['extract_at'])
        cls.quality = {row['experiment_id']: row for row in experiment_quality(cls.raw, cls.events, cls.users)}

    def test_sql_and_pandas_agree(self):
        sql_users = sql_outcomes(self.raw, self.events, self.metadata['extract_at'])
        checks = data_checks(self.raw, self.events, self.users, sql_users, self.metadata['extract_at'])
        self.assertTrue(checks['passed'].all(), checks.to_string(index=False))

    def test_duplicate_events_do_not_inflate_conversions(self):
        repeated = pd.concat([self.events, self.events.head(100)])
        actual = user_outcomes(self.raw, repeated, self.metadata['extract_at'])
        self.assertEqual(int(actual['converted'].sum()), int(self.users['converted'].sum()))
        self.assertEqual(int(actual['purchases_in_window'].sum()), int(self.users['purchases_in_window'].sum()))

    def test_duplicate_assignments_do_not_add_users(self):
        actual = user_outcomes(pd.concat([self.raw, self.raw.head(100)]), self.events, self.metadata['extract_at'])
        self.assertEqual(len(actual), self.raw['user_id'].nunique())

    def test_window_boundaries_and_users_with_no_events(self):
        raw = self.raw.head(2).drop_duplicates('user_id').copy()
        raw['assigned_at'] = '2026-02-01T00:00:00Z'
        times = ['2026-01-31T23:59:59Z', '2026-02-01T00:00:00Z',
                 '2026-02-07T23:59:59Z', '2026-02-08T00:00:00Z']
        events = pd.DataFrame({'user_id': [raw.iloc[0]['user_id']] * 4,
                               'experiment_id': [raw.iloc[0]['experiment_id']] * 4,
                               'event_id': ['a', 'b', 'c', 'd'], 'event_at': times,
                               'event_type': 'purchase'})
        actual = user_outcomes(raw, events, self.metadata['extract_at'])
        independent_sql = sql_outcomes(raw, events, self.metadata['extract_at'])
        self.assertEqual(actual['purchases_in_window'].tolist(), [2, 0])
        self.assertEqual(actual['converted'].tolist(), [1, 0])
        self.assertEqual(independent_sql['purchases_in_window'].sum(), 2)

    def test_itt_keeps_unexposed_treatment_users(self):
        treatment = self.users.loc[self.users['arm'].eq('Treatment')]
        self.assertGreater(treatment['exposed'].eq(0).sum(), 1000)
        result = summarize(treatment)
        self.assertEqual(result['n_t'], len(treatment))

    def test_evaluation_split_is_disjoint(self):
        dev = set(self.users.loc[self.users['split'].eq('Development'), 'user_id'])
        evaluation = set(self.users.loc[self.users['split'].eq('Evaluation'), 'user_id'])
        self.assertTrue(dev.isdisjoint(evaluation))
        self.assertEqual(len(dev | evaluation), len(self.users))

    def test_group_choice_cannot_read_evaluation_outcomes(self):
        changed = self.users.copy()
        selected = select_development_groups(changed)
        changed.loc[changed['split'].eq('Evaluation'), 'converted'] = 1 - changed.loc[changed['split'].eq('Evaluation'), 'converted']
        self.assertEqual(selected, select_development_groups(changed))

    def test_control_baseline_uses_all_control_assignments(self):
        selection = filtered(self.users, 'retargeting', 'Evaluation')
        result = summarize(selection)
        control = selection.loc[selection['arm'].eq('Control')]
        self.assertAlmostEqual(result['y_c'] / result['n_c'], control['converted'].mean())

    def test_broken_extract_is_blocked(self):
        quality = self.quality['missing_controls']
        self.assertTrue(quality['blocked'])
        self.assertLess(quality['srm_p'], 0.001)
        self.assertGreater(quality['missing_assignment_event_users'], 0)

    def test_filter_cannot_clear_full_experiment_failure(self):
        balanced = {'n_t': 10000, 'n_c': 10000, 'y_t': 2000, 'y_c': 1000,
                    'effect': 0.1, 'lower': 0.08, 'upper': 0.12, 'srm_p': 1}
        self.assertEqual(decision(balanced, 0, blocked=True), 'Investigate data')

    def test_main_synthetic_evaluation_result(self):
        result = summarize(filtered(self.users, 'retargeting', 'Evaluation'))
        self.assertGreater(result['lower'], 0)
        self.assertEqual(result['n_t'] + result['n_c'], 60285)
        self.assertEqual(decision(result, self.quality['retargeting']['srm_p']), 'Worth a follow-up rollout')

    def test_small_test_has_an_inconclusive_case(self):
        result = summarize(filtered(self.users, 'small_test', 'Evaluation'))
        self.assertLess(result['lower'], 0)
        self.assertGreater(result['upper'], 0)
        self.assertEqual(decision(result, self.quality['small_test']['srm_p'], cost=0.3), 'Inconclusive at this cost')

    def test_development_does_not_get_a_rollout_recommendation(self):
        result = summarize(filtered(self.users, 'retargeting', 'Development'))
        self.assertEqual(decision(result, self.quality['retargeting']['srm_p'], 'Development'), 'Development only')

    def test_wilson_known_zero_success_case(self):
        lower, upper = wilson_interval(0, 10)
        self.assertAlmostEqual(lower, 0, places=12)
        self.assertAlmostEqual(upper, 0.2775327998628892, places=10)

    def test_zero_conversion_interval_has_width(self):
        effect, lower, upper = difference_interval(100, 0, 100, 0)
        self.assertEqual(effect, 0)
        self.assertLess(lower, 0)
        self.assertGreater(upper, 0)

    def test_interval_reverses_with_the_arms(self):
        effect, lower, upper = difference_interval(1000, 100, 900, 60)
        reverse, r_lower, r_upper = difference_interval(900, 60, 1000, 100)
        self.assertAlmostEqual(effect, -reverse)
        self.assertAlmostEqual(lower, -r_upper)
        self.assertAlmostEqual(upper, -r_lower)

    def test_large_sample_interval_agrees_with_normal_approximation(self):
        effect, lower, upper = difference_interval(100000, 8000, 100000, 7000)
        error = 1.95996398454 * np.sqrt(0.08 * 0.92 / 100000 + 0.07 * 0.93 / 100000)
        self.assertAlmostEqual(lower, effect - error, delta=0.00001)
        self.assertAlmostEqual(upper, effect + error, delta=0.00001)

    def test_no_users_and_missing_arm_are_explicit(self):
        self.assertEqual(difference_interval(0, 0, 100, 10), (None, None, None))
        self.assertEqual(sample_ratio(0, 0), None)
        empty = summarize(self.users.head(0))
        self.assertEqual(decision(empty, 1), 'No users')

    def test_balanced_srm_is_one(self):
        self.assertEqual(sample_ratio(500, 500), 1)
        self.assertLess(sample_ratio(900, 100), 0.001)

    def test_cost_changes_money_without_changing_conversion_effect(self):
        result = summarize(filtered(self.users, 'retargeting', 'Evaluation'))
        baseline = economic_result(result, cost=0.6, contribution=90)
        higher = economic_result(result, cost=1.6, contribution=90)
        self.assertAlmostEqual(baseline['point'] - higher['point'], 1000)
        self.assertEqual(decision(result, 1, cost=5), 'Does not cover assumed cost')

    def test_zero_contribution_has_no_positive_value(self):
        result = summarize(filtered(self.users, 'retargeting', 'Evaluation'))
        self.assertEqual(economic_result(result, 0.6, 0)['point'], -600)
        self.assertEqual(decision(result, 1, contribution=0), 'Does not cover assumed cost')

    def test_smaller_effect_needs_more_users(self):
        self.assertGreater(planned_sample_size(0.07, 0.005), planned_sample_size(0.07, 0.01))
        self.assertEqual(planned_sample_size(0, 0.01), None)
        self.assertEqual(planned_sample_size(0.9, 0.2), None)


if __name__ == '__main__':
    unittest.main()
