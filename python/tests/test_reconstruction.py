"""Independent commutator and finite singular-direction controls."""
import unittest
import numpy as np
from signal_space.numerics.prereception import RadialSystem
from signal_space.numerics.reception_transfer import derivative, frozen_operator
from signal_space.numerics.reconstruction import acquisition, causal_capture, singular_audit


class ReconstructionTests(unittest.TestCase):
    def test_two_site_commutator_equals_dense_projector(self):
        r=np.linspace(0,4,41);system=RadialSystem(r,.2);u=system.r*np.exp(-system.r**2)
        mass,K=frozen_operator(system,u);n=len(mass);matrix=K(np.eye(n)).T
        ix=19;P=np.diag(np.arange(n)<=ix);b=np.sin(system.r*1.7)
        expected=(matrix@P-P@matrix)@b
        actual=np.zeros(n);actual[ix]=-matrix[ix,ix+1]*b[ix+1];actual[ix+1]=matrix[ix+1,ix]*b[ix]
        np.testing.assert_allclose(actual,expected,atol=1e-12)

    def test_causal_capture_matches_independent_source_projection(self):
        r=np.linspace(0,8,81);system=RadialSystem(r,.2);u=system.r*np.exp(-system.r**2)
        x=system.r-5;b=np.where(abs(x)<1,(1-x*x)**4,0.);v=derivative(b,.1)
        surface,source=acquisition(system,u,b,v,.0025,4.,.005,2.)
        trace,captured=causal_capture(system,u,surface,.0025,4.,.005,2.,.2)
        source[:,20:]=0
        self.assertLess(np.linalg.norm(captured-source)/np.linalg.norm(source),2e-7)
        self.assertEqual(trace.shape,(801,3))

    def test_singular_witness_is_surface_admissible(self):
        # Independent two-mode example: weak surface mode directly shifts a tail.
        t=np.linspace(0,6,601);f=np.exp(-(t-3)**2);fd=-2*(t-3)*f
        L=np.zeros((len(t)*2,2));L[::2,0]=f;L[1::2,0]=fd
        L[::2,1]=.1*np.exp(-(t-4)**2);L[1::2,1]=-.2*(t-4)*np.exp(-(t-4)**2)
        H=np.diag([1.,1e-12]);U=np.eye(2);s=np.array([1.,1e-12]);V=np.eye(2);q=np.array([1.,0.])
        p={'amplitude':1.,'local_radius':1.,'marker_threshold':.1,'surface_relative_tolerance':1e-10,'input_radius_factor':2.}
        from signal_space.numerics.reconstruction import markers
        times=markers(t,(L@q).reshape(-1,2),p)
        sensitivity,witnesses=singular_audit(H,L,q,U,s,V,s>1e-10,H@q,times,t,p)
        self.assertEqual(len(sensitivity),2)
        self.assertTrue(all(w['surface_relative_change']<=1.00001e-10 for w in witnesses))
        self.assertTrue(all(w['surface_relative_residual']<=1.00001e-10 for w in witnesses))
        self.assertTrue(any(w['marker_shift'] and max(abs(x) for x in w['marker_shift'])>.01 for w in witnesses))
