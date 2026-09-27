"""Independent dense evolution, interface equivalence and causal-prefix controls."""
import unittest
import numpy as np
from scipy.linalg import expm
from signal_space.numerics.prereception import RadialSystem
from signal_space.numerics.reception_transfer import frozen_operator
from signal_space.numerics.boundary_memory import coefficients,stiffness,source,replay,events


class BoundaryMemoryTests(unittest.TestCase):
    def setUp(self):
        self.r=np.linspace(0,8,41);self.system=RadialSystem(self.r,.2)
        self.u=self.system.r*np.exp(-self.system.r**2/4)
        q=np.maximum(0,1-((self.system.r-5.5)/.7)**2)**4
        self.b=q[None,:];self.v=np.zeros_like(self.b)

    def test_stiffness_matches_hamiltonian_and_dense_exact_evolution(self):
        M,D,O=coefficients(self.system,self.u);mass,K=frozen_operator(self.system,self.u)
        n=len(M);dense=np.diag(D)+np.diag(O,1)+np.diag(O,-1)
        np.testing.assert_allclose(dense,np.stack([K(e) for e in np.eye(n)],axis=1),rtol=1e-14,atol=1e-12)
        F=np.block([[np.zeros((n,n)),np.diag(1/M)],[-dense,np.zeros((n,n))]])
        exact=expm(.2*F)@np.r_[self.b[0],M*self.v[0]]
        measured,_=source(self.system,self.u,self.b,self.v,.002,.2,.002,4,1,True)
        ix=round(1/self.system.h)-1
        np.testing.assert_allclose(measured[-1,0],[exact[ix],exact[n+ix]/M[ix]],atol=1e-12)

    def test_boundary_replay_and_cutoff_are_causal(self):
        dt=.01;duration=4.;sample=.02;cutoff=2.
        surface,_=source(self.system,self.u,self.b,self.v,dt,duration,sample,4,3,False)
        actual,_=source(self.system,self.u,self.b,self.v,dt,duration,sample,4,3,True)
        t=np.arange(len(surface))*sample
        forecast,_=replay(self.system,self.u,t,surface,dt,duration,sample,4,3,cutoff)
        error=np.linalg.norm(forecast[:,0,0,0]-actual[:,0,0])/np.linalg.norm(actual[:,0,0])
        self.assertLess(error,1e-5)
        changed=surface.copy();changed[t>2.2]+=10.
        perturbed,_=replay(self.system,self.u,t,changed,dt,duration,sample,4,3,cutoff)
        np.testing.assert_array_equal(forecast[:,1],perturbed[:,1])
        np.testing.assert_array_equal(forecast[t<=2.],perturbed[t<=2.])

    def test_prospective_excursion_ignores_later_crossings(self):
        t=np.linspace(0,12,1201);a=2e-4*np.sin(t);v=2e-4*np.cos(t)
        pair=events(t,a,v);legacy=events(t,a,v,'legacy')
        self.assertAlmostEqual(pair[0],np.pi/6,places=8)
        self.assertAlmostEqual(pair[1],5*np.pi/6,places=8)
        self.assertGreater(legacy[1],pair[1]+6)
