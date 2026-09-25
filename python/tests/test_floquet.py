import unittest
from pathlib import Path
import numpy as np
from signal_space.models.floquet import background, stages, bloch, apply_tangent
from signal_space.analysis.floquet import physical_reference
from signal_space.experiments.floquet import FloquetExperiment
from signal_space.runtime.io import read_json

class FloquetTests(unittest.TestCase):
    def test_closed_schema_and_identity(self):
        p=FloquetExperiment(); c=read_json(Path(__file__).resolve().parents[2]/'fixtures/research/gross-test-04.json')
        self.assertEqual(p.validate(c),c)
        c['parameters']['cycles']=True
        with self.assertRaises(ValueError): p.validate(c)
    def test_vacuum_fourier_realification(self):
        _,_,blocks=stages('vacuum',1e-5)
        for q in [np.array([.03,-.07,.11]),np.array([.4,.2,-.3])]:
            np.testing.assert_allclose(bloch(blocks,q),physical_reference(q),atol=2e-8)
    def test_periodic_projectors_and_wave(self):
        for label in ('vacuum','equal','counter'):
            inputs,outputs,_=stages(label,1e-5)
            np.testing.assert_allclose(outputs[-1,:2],inputs[0,:2],atol=1e-12)
            for a,b in zip(inputs[:,2],outputs[:,2]):
                np.testing.assert_allclose(np.outer(a,a.conj()),np.outer(b,b.conj()),atol=1e-12)
    def test_bond_phase_matches_explicit_real_stencil(self):
        _,_,blocks=stages('counter',1e-5); size=5
        q=2*np.pi*np.array([1,0,-1])/size
        pos=np.indices((size,)*3).transpose(1,2,3,0)
        seed=np.arange(20)/20
        field=np.exp(1j*(pos@q))[...,None]*seed
        expected=np.exp(1j*(pos@q))[...,None]*(bloch(blocks,q)@seed)
        np.testing.assert_allclose(apply_tangent(field,blocks),expected,atol=1e-10)
    def test_science_failure_is_not_technical_pass(self):
        from signal_space.experiments.floquet import CRITERIA
        p=FloquetExperiment(); checks={'checks':[{'id':k,'status':'pass'} for k in CRITERIA]}
        checks['checks'][-2]['status']='fail';checks['checks'][-1]['status']='unresolved'
        self.assertEqual(p.classify(checks,{}),'fail')
        checks['checks'][0]['status']='fail'
        self.assertEqual(p.classify(checks,{}),'unresolved')
