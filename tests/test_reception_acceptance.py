"""Phase extraction and integrated response checked against full dynamics."""
import unittest
import numpy as np
from signal_space.numerics.prereception import RadialSystem
from signal_space.numerics.reception import evolve
from signal_space.numerics.reception_acceptance import forecast,incident
from signal_space.analysis.reception_acceptance import phase_series,interval,budget


class AcceptanceTests(unittest.TestCase):
    def test_phase_series_handles_winding_and_fourth_order_log(self):
        t=np.linspace(0,40,801);z0=np.exp(.7j*t);z2=(.2+.3j*np.sin(t))*z0;z4=(.04-.08j*np.cos(t))*z0
        errors=[]
        for A in (.2,.1):
            jet=np.zeros((len(t),14));jet[:,1]=z0.real;jet[:,2]=-z0.imag;jet[:,3]=z2.real;jet[:,4]=-z2.imag;jet[:,5]=z4.real;jet[:,6]=-z4.imag
            z=z0+A*A*z2+A**4*z4;full=np.zeros((len(t),12));quiet=full.copy();full[:,1]=z.real;full[:,2]=-z.imag;quiet[:,1]=z0.real;quiet[:,2]=-z0.imag
            actual,_,pred=phase_series(jet,full,quiet,A,1.)
            errors.append(np.linalg.norm(actual-pred))
            np.testing.assert_allclose(actual,np.angle(1+A*A*z2/z0+A**4*z4/z0)/(2*np.pi),atol=1e-15)
        self.assertGreater(errors[0]/errors[1],50)

    def test_integrated_taylor_remainder_and_frozen_null(self):
        r=np.arange(81)*.1;sys=RadialSystem(r,.2);u=.3*sys.r*np.exp(-sys.r**2/3);mode=sys.r*np.exp(-sys.r**2/4)
        p={'packet_centers':[1.4,2.4],'packet_width':.8,'clock_amplitude':.03,'omega_chi':.5,'omega_Q':.9,'local_radius':1.2,'sample_interval':.02,'duration':.4}
        cases=[{'phase':0.,'weights':[1,0],'amplitude':0.}]
        pred=forecast(sys,u,mode,.001,p,cases)[:,0]
        null=forecast(sys,u,mode,.001,p,cases,True)
        np.testing.assert_array_equal(null[:,:,3:7],0.)
        errors=[]
        # Larger fixture amplitudes keep the sixth-order remainder above
        # the ~1e-14 phase roundoff floor; production amplitudes are separate.
        for A in (.6,.3):
            cs=[cases[0],dict(cases[0],amplitude=A)]
            initial=lambda c,rr:tuple(c['amplitude']*x for x in incident(rr,p,c['weights']))
            full,_,_=evolve(sys,u,mode,.001,p,cs,initial)
            actual,_,prediction=phase_series(pred,full[:,1],full[:,0],A,p['omega_chi'])
            errors.append(np.linalg.norm(actual-prediction))
        self.assertGreater(errors[0]/errors[1],30)

    def test_fixed_interval_and_budget_include_independent_controls(self):
        t=np.arange(21)*.5;self.assertAlmostEqual(interval(t,.2*t,[2.,8.]),1.2)
        self.assertAlmostEqual(budget({'finer':10.,'fine':9.,'time':8.5,'base':7.,'wide':6.8},.01),1.71)
        with self.assertRaises(ValueError):interval(t,t,[2.,11.])
