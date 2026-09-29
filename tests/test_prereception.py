"""Independent Hamiltonian and Taylor-order checks; no scientific pass asserted."""
import unittest
import numpy as np
from signal_space.numerics.prereception import RadialSystem, packet

class PrereceptionControls(unittest.TestCase):
    def test_neutral_reciprocity_and_hamiltonian(self):
        rng=np.random.default_rng(19);r=np.linspace(0,8,81);sys=RadialSystem(r,.2)
        y=(rng.normal(size=(6,1,79))+1j*rng.normal(size=(6,1,79)))*.02
        y[2:]=y[2:].real;y[0]+=r[1:-1]*.4
        f=sys.rhs(y)
        # Analytic continuous-time energy derivative of the full discrete action
        # independently approximated along its vector field.
        dh=1e-6
        derivative=(sys.energy_charge(y+dh*f)[0]-sys.energy_charge(y-dh*f)[0])/(2*dh)
        self.assertLess(abs(derivative[0]),2e-6)
    def test_taylor_coefficient_and_sign(self):
        rng=np.random.default_rng(28);r=np.linspace(0,8,81);sys=RadialSystem(r,.2)
        y=np.zeros((10,1,79),complex);y[0]=r[1:-1]*.5;y[1]=-.9j*y[0]
        y[2]=.001*r[1:-1];y[4:6]=rng.normal(size=(2,1,79))*.1
        y[6:]=rng.normal(size=(4,1,79))*.01
        tangent=sys.rhs(y,True)
        baseline=y[:6].copy();baseline[4:6]=0
        a=1e-4; full=baseline.copy();full[:4]+=a*a*y[6:];full[4:6]=a*y[4:6]
        expected=(sys.rhs(full)[:4]-sys.rhs(baseline)[:4])/a**2
        np.testing.assert_allclose(expected,tangent[6:],rtol=1e-4,atol=2e-5)
        flip=full.copy();flip[4:6]*=-1
        np.testing.assert_array_equal(sys.rhs(full)[:4],sys.rhs(flip)[:4])
    def test_compact_packet(self):
        r=np.linspace(0,80,801);b,v=packet(r,18,3)
        self.assertTrue(np.all(b[abs(r-18)>=3]==0))
        self.assertTrue(np.all(v[abs(r-18)>=3]==0))

if __name__=='__main__':unittest.main()
