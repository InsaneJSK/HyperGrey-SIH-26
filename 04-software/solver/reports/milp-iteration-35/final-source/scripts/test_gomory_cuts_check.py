import copy
import unittest
from check_gomory_cuts import check


def fixture():
    return {'cuts': 14,
            'gomory_cuts': {'enabled': True, 'calls': 3, 'candidates': 40, 'attempts': 24, 'generated': 18,
                            'applied': 18, 'purged': 6, 'rounds': 3, 'basis_rejected': 0, 'skipped_free': 1,
                            'skipped_drop': 0, 'skipped_consistency': 0, 'skipped_dynamism': 2,
                            'skipped_support': 1, 'skipped_efficacy': 1, 'skipped_parallel': 1,
                            'rejected_incumbent': 0, 'best_efficacy': 0.31, 'seconds': 0.4}}


def quiet():
    return {'cuts': 0,
            'gomory_cuts': {'enabled': False, 'calls': 0, 'candidates': 0, 'attempts': 0, 'generated': 0,
                            'applied': 0, 'purged': 0, 'rounds': 0, 'basis_rejected': 0, 'skipped_free': 0,
                            'skipped_drop': 0, 'skipped_consistency': 0, 'skipped_dynamism': 0,
                            'skipped_support': 0, 'skipped_efficacy': 0, 'skipped_parallel': 0,
                            'rejected_incumbent': 0, 'best_efficacy': 0, 'seconds': 0}}


class Checks(unittest.TestCase):
    def test_valid(self):
        result = check(fixture())
        self.assertTrue(result['all_pass'])
        self.assertEqual(result['retained'], 12)

    def test_disabled(self):
        result = check(quiet())
        self.assertTrue(result['all_pass'])
        self.assertFalse(result['enabled'])

    def test_disabled_work(self):
        for key in ('calls', 'attempts', 'applied', 'seconds', 'best_efficacy'):
            with self.subTest(key=key):
                r = quiet(); r['gomory_cuts'][key] = 1
                with self.assertRaises(AssertionError):
                    check(r)

    def test_invalid(self):
        for key, value in [('attempts', 41), ('generated', 25), ('applied', 19), ('purged', 19),
                           ('rounds', 19), ('calls', -1), ('seconds', float('nan')), ('seconds', -1),
                           ('candidates', True), ('enabled', 1), ('best_efficacy', float('inf'))]:
            with self.subTest(key=key):
                r = fixture(); r['gomory_cuts'][key] = value
                with self.assertRaises(AssertionError):
                    check(r)

    def test_outcomes_must_fit_attempts(self):
        r = fixture(); r['gomory_cuts']['skipped_dynamism'] = 20
        with self.assertRaises(AssertionError):
            check(r)

    def test_efficacy_pairs_with_cuts(self):
        r = fixture(); r['gomory_cuts']['best_efficacy'] = 0
        with self.assertRaises(AssertionError):
            check(r)
        r = fixture(); r['gomory_cuts']['applied'] = 0; r['gomory_cuts']['purged'] = 0
        r['gomory_cuts']['rounds'] = 0
        with self.assertRaises(AssertionError):
            check(r)

    def test_retained_cannot_exceed_total(self):
        r = copy.deepcopy(fixture()); r['cuts'] = 5
        with self.assertRaises(AssertionError):
            check(r)

    def test_missing_section(self):
        with self.assertRaises(AssertionError):
            check({'cuts': 0})


if __name__ == '__main__':
    unittest.main()
