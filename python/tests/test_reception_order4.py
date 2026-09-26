"""Independent coefficient check against the unchanged nonlinear discrete RHS."""
import unittest
import numpy as np
from signal_space.numerics.prereception import RadialSystem
from signal_space.numerics.reception_order4 import jet_rhs


class FormalResponseTest(unittest.TestCase):
    def test_truncation_has_the_predicted_parity_and_order(self):
        r=np.arange(41)*.1;sys=RadialSystem(r,.2);x=sys.r
        wave=lambda c,w:np.exp(-((x-c)/w)**2)
        y=np.zeros((16,len(x)),complex)
        y[0]=.25*wave(1.3,.6)*(1+.2j);y[1]=-.9j*y[0]
        y[2]=.03*wave(1.8,.7);y[3]=-.004*wave(2.2,.9)
        y[4]=.8*wave(2,.8);y[5]=.12*wave(1.6,.8)
        y[6]=(.15+.08j)*wave(1.5,.7);y[7]=(.02-.04j)*wave(1.1,.6)
        y[8]=.025*wave(1.7,.7);y[9]=.005*wave(2.1,.8)
        y[10]=.17*wave(2.3,.8);y[11]=-.13*wave(1.6,.7)
        y[12]=(.022+.011j)*wave(1.4,.9);y[13]=(.007-.003j)*wave(1.7,.6)
        y[14]=.007*wave(2,.7);y[15]=-.009*wave(1.8,.8)
        coefficients=jet_rhs(sys,y)
        quiet=np.zeros((6,len(x)),complex);quiet[:4]=y[:4]
        base=sys.rhs(quiet)
        def errors(A):
            state=np.zeros_like(quiet)
            state[:4]=y[:4]+A*A*y[6:10]+A**4*y[12:16]
            state[4:]=A*y[4:6]+A**3*y[10:12]
            actual=sys.rhs(state)
            charged=actual[1]-base[1]-A*A*coefficients[7]-A**4*coefficients[13]
            clock=actual[3]-base[3]-A*A*coefficients[9]-A**4*coefficients[15]
            neutral=actual[4:6]-A*coefficients[4:6]-A**3*coefficients[10:12]
            return np.linalg.norm(charged),np.linalg.norm(clock),np.linalg.norm(neutral)
        coarse=errors(.16);fine=errors(.08)
        self.assertGreater(coarse[0]/fine[0],40)  # charged remainder O(A^6)
        self.assertGreater(coarse[1]/fine[1],40)  # clock remainder O(A^6)
        self.assertGreater(coarse[2]/fine[2],25)  # neutral remainder O(A^5)


if __name__=='__main__':unittest.main()
