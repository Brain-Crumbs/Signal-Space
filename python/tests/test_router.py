"""Independent limiting cases and adversarial classifier/config boundaries."""
import unittest
from copy import deepcopy
import numpy as np
from signal_space.models.router import stencil, fourier, apply_shifts
from signal_space.analysis.router import reference_phase, quaternion
from signal_space.experiments.router import RouterExperiment, CRITERIA


class RouterTests(unittest.TestCase):
    def test_collinear_is_exact_translation_of_components(self):
        rng=np.random.default_rng(40)
        field=rng.normal(size=(5,5,5,2))+1j*rng.normal(size=(5,5,5,2))
        triad=np.array([[0,0,1]]*3)
        out=apply_shifts(field,triad,[0,1,2])
        expected=np.stack([np.roll(field[...,0],(1,1,1),axis=(0,1,2)),np.roll(field[...,1],(-1,-1,-1),axis=(0,1,2))],axis=-1)
        np.testing.assert_allclose(out,expected,atol=1e-14)
        shifts,coeff=stencil(triad,[0,1,2]); q=np.array([[.13,-.27,.41]])
        np.testing.assert_allclose(fourier(q,shifts,coeff)[0],np.diag(np.exp([-1j*q.sum(),1j*q.sum()])),atol=1e-14)

    def test_order_sign_and_extra_nodes(self):
        n=np.eye(3); q=np.array([[.3,.4,.5]])
        a,_=quaternion(q,n,[0,1,2]); b,_=quaternion(q,n,[2,1,0])
        self.assertAlmostEqual(float(a[0]-b[0]),float(2*np.sin(q).prod()),places=14)
        nodes=np.array([[0,0,0],[-np.pi,0,0],[-np.pi,-np.pi,0],[np.pi/2,np.pi/2,np.pi/2]])
        np.testing.assert_allclose(reference_phase(nodes,n,[0,1,2]),[0,np.pi,0,0],atol=1e-14)

    def test_analytic_derivative_axial_limit(self):
        q=np.array([[.2,0,0]]); a,b=quaternion(q,np.eye(3),[0,1,2]); da,db=quaternion(q,np.eye(3),[0,1,2],0)
        bn=np.linalg.norm(b,axis=1)
        grad=(a*np.sum(b*db,axis=1)/bn-bn*da)/(a*a+bn*bn)
        self.assertAlmostEqual(float(grad[0]),1,places=14)

    def test_config_closed_and_classification_not_assumed(self):
        plugin=RouterExperiment(); config=plugin.schema()['default']; plugin.validate(config)
        bad=deepcopy(config); bad['parameters']['orders']['forward']=[2,1,0]
        with self.assertRaises(ValueError): plugin.validate(bad)
        bad=deepcopy(config); bad['parameters']['orders']['forward']=[0, True, 2]
        with self.assertRaises(ValueError): plugin.validate(bad)
        checks={'checks':[{'id':k,'status':'pass'} for k in CRITERIA]}
        self.assertEqual(plugin.classify(checks,config),'pass')
        checks['checks'][-1]['status']='fail'; self.assertEqual(plugin.classify(checks,config),'fail')
        checks['checks'].pop(); self.assertEqual(plugin.classify(checks,config),'unresolved')
