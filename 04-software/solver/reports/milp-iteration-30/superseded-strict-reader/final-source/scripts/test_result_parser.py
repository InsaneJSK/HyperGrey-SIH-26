"""Regression for unsolicited native reference-solver stdout diagnostics."""
import json
import unittest
from benchmark_lp import parse_json_output


class ResultParserTests(unittest.TestCase):
    def test_plain_and_formatted(self):
        for indent in (None, 2):
            self.assertEqual(parse_json_output(json.dumps({'status': 'Optimal'}, indent=indent)), {'status': 'Optimal'})

    def test_native_diagnostics_are_retained(self):
        result = parse_json_output('native prefix\n{"status":"Optimal","objective":7.598985}\nnative suffix\n')
        self.assertEqual(result['objective'], 7.598985)
        self.assertEqual(result['stdout_diagnostics'], 'native prefix\nnative suffix')

    def test_ambiguous_or_missing_result_fails(self):
        for output in ('noise', '{"status":"Optimal"}\n{"status":"Failed"}', '[]'):
            with self.assertRaises(ValueError):
                parse_json_output(output)


if __name__ == '__main__':
    unittest.main()
