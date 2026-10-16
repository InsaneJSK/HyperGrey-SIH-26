import unittest
from milp_robustness import classify


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.ours = dict(status='optimal', objective=10., best_bound=10., gap=0., primal=[1.], rows=1, columns=1)
        self.ref = dict(status='Optimal', objective=10., gap=0., maximize=False, columns=1, rows=1,
                        candidate_checked=True, candidate_max_violation=0., candidate_integer_violation=0., candidate_objective=10.)

    def category(self, exact=False):
        return classify(self.ours, self.ref, 1e-6, exact)[0]

    def test_numeric_not_exact(self):
        self.assertEqual(self.category(), 'numerical_completion_checked')

    def test_exact_separate(self):
        self.assertEqual(self.category(True), 'exact_proof_checked')

    def test_point_is_not_proof(self):
        self.ours.update(status='time_limit', best_bound=9., gap=1/11)
        self.assertEqual(self.category(), 'feasible_limit')

    def test_no_saved_point(self):
        self.ours.update(status='time_limit', primal=[], objective=None, gap=None)
        self.assertEqual(self.category(), 'no_incumbent_limit')

    def test_reference_pending(self):
        self.ref.update(status='Time limit reached', gap=.1)
        self.assertEqual(self.category(), 'completion_reference_pending')

    def test_bad_point(self):
        self.ref['candidate_max_violation'] = .01
        self.assertEqual(self.category(), 'validation_failure')

    def test_bad_integrality(self):
        self.ref['candidate_integer_violation'] = .1
        self.assertEqual(self.category(), 'validation_failure')

    def test_false_optimum(self):
        self.ref['objective'] = 9.
        self.assertEqual(self.category(), 'validation_failure')

    def test_gap_limit_allows_requested_accuracy(self):
        self.ours.update(status='gap_limit', objective=10.000005, best_bound=10., gap=.000005/11.000005)
        self.ref['candidate_objective'] = self.ours['objective']
        self.assertEqual(self.category(), 'numerical_completion_checked')

    def test_max_gap_limit_allows_requested_accuracy(self):
        self.ref['maximize'] = True
        self.ours.update(status='gap_limit', objective=9.999995, best_bound=10., gap=.000005/10.999995)
        self.ref['candidate_objective'] = self.ours['objective']
        self.assertEqual(self.category(), 'numerical_completion_checked')

    def test_wrong_sense_bound(self):
        self.ours.update(status='time_limit', best_bound=11., gap=0.)
        self.assertEqual(self.category(), 'validation_failure')

    def test_maximization_bound(self):
        self.ref['maximize'] = True
        self.ours.update(status='time_limit', best_bound=12., gap=2/11)
        self.assertEqual(self.category(), 'feasible_limit')
        self.ours.update(best_bound=9., gap=0.)
        self.assertEqual(self.category(), 'validation_failure')

    def test_false_infeasibility(self):
        self.ours.update(status='infeasible', primal=[], objective=None, best_bound=None, gap=None)
        self.assertEqual(self.category(), 'validation_failure')

    def test_reference_error_with_point(self):
        self.ours.update(status='time_limit')
        self.ref = dict(status='process_error')
        self.assertEqual(self.category(), 'incumbent_reference_pending')

    def test_missing_completion_bound(self):
        self.ours['best_bound'] = None
        self.assertEqual(self.category(), 'validation_failure')

    def test_input_rejected(self):
        self.ours = dict(status='process_error', stderr='error: MPS line 9: Unsupported bound type')
        self.assertEqual(self.category(), 'input_rejected')


if __name__ == '__main__':
    unittest.main()
