from __future__ import print_function
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import FullFactorialDriver  # FullFactorialDriver driver
from openmdao.api import ExecComp  # 'Quick Component' - useful for creating constraints
from openmdao.api import SubProblem  # Allows for nested drivers - not currently supported in OpenMETA - Introduced in OpenMDAO v.1.7.2.
from openmdao.api import SqliteRecorder  # Recorder
import sqlitedict  
from pprint import pprint

import timeit  # Used for timing/performance tests

# mockup version of subproblem nested within top level problem
class mockup_subproblem(Component):

    def __init__(self):
        super(mockup_subproblem, self).__init__()
        
        self.add_param('y', val=0.0)
        
        self.add_output('f_xy', shape=1)
        
    def solve_nonlinear(self, params, unknowns, resids):
        unknowns['f_xy'] = params['y']