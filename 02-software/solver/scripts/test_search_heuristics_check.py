import copy
import unittest
from check_search_heuristics import check


def fixture():
    return {'primal': [1.0], 'first_incumbent_seconds': 0.5,
            'tree_dives': {'enabled': True, 'calls': 4, 'improvements': 1, 'seconds': 0.2},
            'fix_propagate': {'enabled': True, 'calls': 3, 'fixings': 40, 'lps': 2, 'successes': 1, 'seconds': 0.1}}


class Checks(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(check(fixture())['all_pass'])

    def test_invalid(self):
        for section, key, value in [('tree_dives', 'improvements', 5), ('tree_dives', 'calls', -1),
                                    ('tree_dives', 'seconds', float('nan')), ('fix_propagate', 'lps', 4),
                                    ('fix_propagate', 'successes', 3), ('fix_propagate', 'fixings', True),
                                    ('tree_dives', 'enabled', 1)]:
            with self.subTest(section=section, key=key):
                r = fixture(); r[section][key] = value
                with self.assertRaises(AssertionError):
                    check(r)

    def test_disabled_work(self):
        for section in ('tree_dives', 'fix_propagate'):
            r = fixture(); r[section]['enabled'] = False
            with self.assertRaises(AssertionError):
                check(r)

    def test_requires_incumbent(self):
        r = fixture(); r['first_incumbent_seconds'] = None
        with self.assertRaises(AssertionError):
            check(r)
        r = fixture(); r['primal'] = []
        with self.assertRaises(AssertionError):
            check(r)

    def test_quiet(self):
        r = fixture()
        r['tree_dives'] = {'enabled': False, 'calls': 0, 'improvements': 0, 'seconds': 0}
        r['fix_propagate'] = {'enabled': False, 'calls': 0, 'fixings': 0, 'lps': 0, 'successes': 0, 'seconds': 0}
        self.assertTrue(check(copy.deepcopy(r))['all_pass'])


if __name__ == '__main__':
    unittest.main()
