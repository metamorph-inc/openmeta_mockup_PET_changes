'''
# Name: sub_v1.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 7/13/2017
# Edit Date: 7/13/2017

# Tutorial: Problem containing an Optimization driver and a Component
#           Adaption of OpenMDAO tutorial: http://openmdao.readthedocs.io/en/1.7.3/usr-guide/tutorials/paraboloid-tutorial.html

# Inputs:

# Outputs:
'''

from __future__ import print_function
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer  # Optimizer driver
from openmdao.api import ExecComp
from openmdao.api import SqliteRecorder  # Recorder
import sqlitedict
from pprint import pprint

# PythonWrapper Components
class Paraboloid(Component):
    ''' Evaluates the equation f(x,y) = (x-3)^2 +xy +(y+4)^2 - 3 '''

    def __init__(self):
        super(Paraboloid, self).__init__()
        
        self.add_param('x', val=0.0)
        self.add_param('y', val=0.0)
        
        self.add_output('f_xy', shape=1)
        
    def solve_nonlinear(self, params, unknowns, resids):
        ''' f(x,y) = (x-3)^2 + xy + (y+4)^2 - 3 '''
        
        x = params['x']
        y = params['y']
        
        unknowns['f_xy'] = (x-3.0)**2 + x*y + (y+4.0)**2 - 3.0

        
if __name__ == '__main__':

    # Instantiate a Problem 'sub'
    # Instantiate a Group and add it to sub
    sub = Problem()
    sub.root = Group()
    
    # Add the 'Paraboloid' Component to sub's root Group.
    sub.root.add('Paraboloid', Paraboloid())
    
    # Initialize x as a IndepVarComp and add it to sub's root group as 'p1.x'
    # p1.x and p2.y_i are initialized to 0.0 since neither was explicity initialized
    # and they both have ranges of -50 to +50. Default initialization: (+50 - (-50)) / 2.0 = 0
    sub.root.add('p1', IndepVarComp('x', 0.0))  
    sub.root.add('p2', IndepVarComp('y_i', 0.0))
    
    # Initialize z as a IndepVarComp and add it to sub's root group as 'p3.z'
    # Not sure if we will support running PETs with un-driven Problem Inputs but let's initialize it to 0.0
    sub.root.add('p3', IndepVarComp('z', 0.0))
    
    # Connect components
    sub.root.connect('p1.x', 'Paraboloid.x')
    sub.root.connect('p2.y_i', 'Paraboloid.y')
    
    # Add ExecComps for all the Problem Inputs connected directly to Problem Outputs
    # It seems reasonable to use the OpenMETA Problem Output's name as the output
    sub.root.add('output1', ExecComp('y_f = input'))
    sub.root.add('output2', ExecComp('z = input'))
    
    # Connect each IndepVarComp associated with Problem Inputs to its respective Problem Outputs
    sub.root.connect('p2.y_i','output1.input')
    sub.root.connect('p3.z','output2.input')
    
    # Add driver
    sub.driver = ScipyOptimizer()
    
    # Modify the optimization driver's settings
    sub.driver.options['optimizer'] = 'COBYLA'      # Type of Optimizer. 'COBYLA' does not require derivatives
    sub.driver.options['tol'] = 1.0e-4              # Tolerance for termination. Not sure exactly what it represents. Default: 1.0e-6
    sub.driver.options['maxiter'] = 200             # Maximum iterations. Default: 200
    #sub.driver.opt_settings['rhobeg'] = 1.0        # COBYLA-specific setting. Initial step size. Default: 1.0
    #sub.driver.opt_settings['catol'] = 0.1         # COBYLA-specific setting. Absolute tolerance for constraint violations. Default: 0.1
    
    # Add design variables, objective, and constraints to the optimization driver
    sub.driver.add_desvar('p1.x', lower=-50, upper=50)
    sub.driver.add_desvar('p2.y_i', lower=-50, upper=50)
    sub.driver.add_objective('Paraboloid.f_xy')
    
    
    # Data collection
    recorder = SqliteRecorder('record_results')
    recorder.options['record_params'] = True
    recorder.options['record_metadata'] = True
    sub.driver.add_recorder(recorder)
    
    # Setup, run, & cleanup
    sub.setup(check=False)
    sub.run()
    sub.cleanup()
    
    # Data retrieval & display
    # Old way - good for debugging IndepVars
    db = sqlitedict.SqliteDict( 'record_results', 'iterations' )
    db_keys = list( db.keys() ) # list() needed for compatibility with Python 3. Not needed for Python 2
    for i in db_keys:
        data = db[i]
        print('\n')
        print(data['Unknowns'])
        print(data['Parameters'])