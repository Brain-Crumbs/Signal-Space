"""Independent physical controls for the versioned Test 5 action audit."""
import unittest
import numpy as np
from signal_space.models.continuum import lagrangian, metric
from signal_space.numerics.continuum import hessian, orientation_control, gravity_control
from signal_space.experiments.continuum import ContinuumExperiment


class ContinuumControls(unittest.TestCase):
    def test_shifted_coframe_cross_derivative_and_neutral_coupling(self):
        e=np.eye(4)
        e[1,0]=0.2
        inv=np.linalg.inv(metric(e))
        f=np.array([.5,.3,-.2,.1,.7,.4]); grad=np.zeros((6,4))
        h=hessian(f,inv)
        self.assertGreater(abs(h[4,0,4,1]),.1)
        self.assertAlmostEqual(h[4,0,4,1]/h[0,0,0,1],1+.1*np.dot(f[:4],f[:4])/2,places=12)
        # Nonzero neutral gradient changes the core force through Z_s.
        grad[4,0]=1
        step=1e-25
        shifted=f.astype(complex);shifted[0]+=1j*step
        force=-np.imag(lagrangian(shifted,grad,inv))/step
        shifted=f.astype(complex);shifted[0]+=1j*step
        neutral_off=grad.copy();neutral_off[4]=0
        force_off=-np.imag(lagrangian(shifted,neutral_off,inv))/step
        self.assertAlmostEqual(force_off-force,.1*f[0]*inv[0,0]/2,places=12)

    def test_distinct_quartic_control_and_gravity_constraint(self):
        kt,kx,speed=orientation_control()
        self.assertAlmostEqual(kt,1+.4*.6**2,places=12)
        self.assertAlmostEqual(kx,1,places=12)
        self.assertLess(speed,1)
        self.assertLess(gravity_control(),1e-12)

    def test_reject_config_drift(self):
        experiment=ContinuumExperiment(); config=experiment.schema()['default']
        config['parameters']['samples']=201
        with self.assertRaises(ValueError): experiment.validate(config)


if __name__=='__main__': unittest.main()
