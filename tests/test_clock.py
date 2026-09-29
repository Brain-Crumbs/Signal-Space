"""Independent short controls for the flat Test 6 radial clock."""
import unittest
import numpy as np
from signal_space.analysis.clock import oscillation
from signal_space.experiments.clock import ClockExperiment
from signal_space.numerics.clock import profile, eigenproblem, evolution


class BoundClockControls(unittest.TestCase):
    def test_short_local_trace_and_no_well(self):
        r,u,attempts=profile(.9,40.,.2)
        self.assertIsNotNone(u,attempts)
        eigen,mode,_=eigenproblem(r,u,.2,.4)
        no_well,_,_=eigenproblem(r,u,.2,0.)
        self.assertLess(eigen[0],.25)
        self.assertGreaterEqual(no_well[0],.25)
        trace,details=evolution(r,u,mode,.9,eigen[0],.001,.2,.04,3,10,30.)
        null,_=evolution(r,u,mode,.9,eigen[0],0.,.2,.04,3,10,30.)
        self.assertEqual(float(np.max(abs(null[:,1]))),0.)
        local=oscillation(trace)
        self.assertGreater(local['crossings'],2)
        self.assertLess(abs(local['frequency']/np.sqrt(eigen[0])-1),.01)
        self.assertGreater(details['initial_mode_energy'],0)

    def test_config_is_closed(self):
        plugin=ClockExperiment();config=plugin.schema()['default']
        config['parameters']['nu']=.2
        with self.assertRaises(ValueError):plugin.validate(config)


if __name__=='__main__':unittest.main()
