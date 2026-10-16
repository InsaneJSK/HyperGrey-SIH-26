import copy
import unittest
from check_bounded_lp import check, COUNTS


def fixture():
    section = dict.fromkeys(COUNTS, 0)
    section.update(enabled=True, calls=10, warm=8, cold=2, optimal=6, infeasible=2, cutoffs=1, cutoff_nodes=1,
                   failures=1, fallbacks=1, iterations=40, dual_iterations=30, primal_iterations=5, flips=3,
                   refactors=12, prepared=1, seconds=.01)
    return {'status': 'time_limit', 'lp_iterations': 50, 'bounded_lp': section}


class Checks(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(check(fixture())['all_checks_pass'])

    def test_invalid_counts(self):
        for key, value in [('calls', -1), ('warm', 11), ('optimal', 9), ('fallbacks', 2), ('cutoff_nodes', 2),
                           ('dual_iterations', 60), ('prepared', 0), ('flips', True), ('seconds', float('nan')),
                           ('seconds', -1.0), ('iterations', 1.5)]:
            with self.subTest(key=key, value=value):
                r = fixture(); r['bounded_lp'][key] = value
                with self.assertRaises(AssertionError):
                    check(r)

    def test_missing(self):
        r = fixture(); del r['bounded_lp']
        with self.assertRaises(AssertionError):
            check(r)

    def test_disabled(self):
        r = fixture(); r['bounded_lp']['enabled'] = False
        with self.assertRaises(AssertionError):
            check(r)
        quiet = copy.deepcopy(r)
        for key in COUNTS:
            quiet['bounded_lp'][key] = 0
        self.assertFalse(check(quiet)['enabled'])


if __name__ == '__main__':
    unittest.main()
