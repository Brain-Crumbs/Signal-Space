"""Independent inversion, phase and local-marker checks; no desired science asserted."""
import unittest
import numpy as np
from signal_space.numerics.reception import reconstruct, profile, evolve
from signal_space.numerics.prereception import RadialSystem
from signal_space.analysis.reception import markers, phase, interval

class ReceptionControls(unittest.TestCase):
    def test_incoming_is_separated_from_arbitrary_outgoing(self):
        R=14.;t=np.linspace(0,16,1601);F=np.sin(np.pi*t/16)**4
        dF=4*np.sin(np.pi*t/16)**3*np.cos(np.pi*t/16)*np.pi/16
        G=.3*np.sin(2*t);dG=.6*np.cos(2*t)
        surface=np.column_stack((t,(F+G)/R,(dF+dG)/R,(dF-dG-(F+G)/R)/R))
        r=np.linspace(14,30,801);b,v,info=reconstruct(surface,r,R)
        np.testing.assert_allclose(b,np.sin(np.pi*(r-R)/16)**4,atol=1e-10)
        np.testing.assert_allclose(info['incoming'],dF,atol=1e-14)
        np.testing.assert_allclose(info['outgoing'],dG,atol=1e-14)
    def test_local_phase_and_marker_translation(self):
        t=np.linspace(0,20,2001);omega=.4;shift=.02
        base=phase(np.cos(omega*t),-omega*np.sin(omega*t),omega)
        actual=phase(np.cos((omega+shift)*t),-(omega+shift)*np.sin((omega+shift)*t),omega+shift)
        pulse=np.maximum(0,1-abs(t-10)/5);events=markers(t,pulse,.5)
        self.assertAlmostEqual(events[0],7.5);self.assertAlmostEqual(events[1],12.5)
        self.assertAlmostEqual(interval(t,actual-base,events),shift*5/(2*np.pi))
        self.assertIsNone(markers(t,np.zeros_like(t),.5))
    def test_short_solver_shapes_and_zero_neutral_null(self):
        r=np.linspace(0,8,81);u=.01*r[1:-1]*np.exp(-r[1:-1]);mode=r[1:-1]*np.exp(-r[1:-1])
        p={'clock_amplitude':.001,'omega_chi':.4,'duration':.2,'local_radius':.1,'sample_interval':.1}
        c=[{'phase':0.,'weights':[1,0]}]
        rec,fields,rr=evolve(RadialSystem(r,.2),u,mode,.01,p,c,lambda c,r:(np.zeros_like(r),np.zeros_like(r)),True)
        self.assertEqual(rec.shape,(3,1,12));self.assertEqual(fields.shape[2],1)
        np.testing.assert_array_equal(rec[:,:,3:5],0);np.testing.assert_array_equal(rec[:,:,9:12],0)

if __name__=='__main__':unittest.main()
