"""Independent matrix identity and shape-blind reconstruction controls."""
import unittest
import numpy as np
from signal_space.numerics.prereception import RadialSystem
from signal_space.numerics.reception_transfer import (
    observation_matrix, acquire_surface, derivative, invert_surface, frozen_operator)


class DiscreteTransferTests(unittest.TestCase):
    def test_adjoint_matches_dense_rk4_polynomial(self):
        r=np.linspace(0,4,41);system=RadialSystem(r,.2);u=system.r*np.exp(-system.r**2)
        M,K=frozen_operator(system,u);n=len(M);eye=np.eye(n)
        dense=K(eye).T
        np.testing.assert_allclose(dense,dense.T,atol=1e-12)
        F=np.block([[np.zeros((n,n)),np.diag(1/M)],[-dense,np.zeros((n,n))]])
        dt=.01;T=dt*F;P=np.eye(2*n)+T+T@T/2+T@T@T/6+T@T@T@T/24
        H,mask=observation_matrix(system,u,dt,.2,.05,1.,[2.,3.])
        b=np.zeros(n);b[mask]=np.sin(np.arange(mask.sum())*.71);v=derivative(b,.1)
        state=np.r_[b,M*v];rows=[];ix=9
        for k in range(21):
            if k%5==0:rows.extend([state[ix],state[n+ix]/M[ix]])
            state=P@state
        np.testing.assert_allclose(H@b[mask],rows,rtol=1e-11,atol=1e-12)

    def test_inverse_uses_surface_without_shape(self):
        r=np.linspace(0,8,81);system=RadialSystem(r,.2);u=system.r*np.exp(-system.r**2)
        H,mask=observation_matrix(system,u,.01,4.,.02,2.,[4.,6.])
        b=np.zeros(len(system.r));x=system.r[mask]-5
        b[mask]=(1-x*x)**4*np.cos(1.7*x);v=derivative(b,.1)
        surface=acquire_surface(system,u,b,v,.01,4.,.02,2.)
        recovered,rv,info=invert_surface(system,H,mask,surface,1e-10)
        self.assertLess(info['relative_surface_residual'],1e-9)
        check=acquire_surface(system,u,recovered,rv,.01,6.,.02,.2)
        truth=acquire_surface(system,u,b,v,.01,6.,.02,.2)
        self.assertLess(np.linalg.norm(check-truth)/np.linalg.norm(truth),1e-6)
