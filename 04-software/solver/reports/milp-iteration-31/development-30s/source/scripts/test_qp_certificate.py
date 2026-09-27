"""Adversarial tests for the independent checker, not for an optimizer."""
import math
from pathlib import Path
import tempfile
import unittest
from qp_certificate import check
from test_qp_equalities import write_model


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.model=Path(self.temp.name)/'test.qplib'
        write_model(self.model,[2,2],[0,0],[[(0,1),(1,1)]],[2],[-math.inf,-math.inf],[math.inf,math.inf],offset=3)
        self.valid={'primal':[1,1],'row_dual':[-2]}

    def test_valid_and_objective_not_trusted(self):
        result=check(self.model,{**self.valid,'status':'error','objective':-999})
        self.assertTrue(result['diagonal_certificate_passed']);self.assertAlmostEqual(result['recomputed_objective'],5)
        self.assertAlmostEqual(result['dual_bound_minimization_sense'],5)

    def test_infeasible_stationary_point(self):
        result=check(self.model,{'primal':[0,0],'row_dual':[0]})
        self.assertFalse(result['independent_kkt_passed']);self.assertEqual(result['stationarity'],0)

    def test_feasible_nonstationary_point(self):
        self.assertFalse(check(self.model,{'primal':[.5,1.5],'row_dual':[-2]})['diagonal_certificate_passed'])

    def test_missing_dual_and_nonfinite_rejected(self):
        for candidate in ({'primal':[1,1]}, {'primal':[1,math.nan],'row_dual':[-2]}, {'primal':[1,1],'row_dual':[math.inf]}):
            self.assertFalse(check(self.model,candidate)['candidate_valid_shape_and_finite'])

    def test_maximize_bound_uses_minimization_sense(self):
        write_model(self.model,[2,2],[0,0],[[(0,1),(1,1)]],[2],[-math.inf]*2,[math.inf]*2,maximize=True,offset=3)
        result=check(self.model,self.valid)
        self.assertTrue(result['diagonal_certificate_passed']);self.assertAlmostEqual(result['recomputed_objective'],-5)
        self.assertAlmostEqual(result['dual_bound_minimization_sense'],5)

    def test_infinite_row_endpoint_dual_sign_rejected(self):
        # Modify only the fixture's lower equality into a one-sided upper row.
        text=self.model.read_text();text=text.replace('1e100\n0\n1\n1 2\n','1e100\n0\n1\n1 -1e100\n',1);self.model.write_text(text)
        self.assertFalse(check(self.model,self.valid)['diagonal_certificate_passed'])

    def test_false_small_gradient_requires_dual_gap(self):
        # Tiny curvature and huge box: projected-gradient tolerance alone can
        # accept a point whose objective is far from the separable optimum.
        write_model(self.model,[1e-16,1],[0,0],[[(1,1)]],[0],[-1e12,-1],[1e12,1])
        result=check(self.model,{'primal':[1e8,0],'row_dual':[0]})
        self.assertTrue(result['independent_kkt_passed']);self.assertFalse(result['diagonal_certificate_passed'])


if __name__=='__main__':unittest.main()
