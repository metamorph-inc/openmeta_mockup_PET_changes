'''
# Name: sub_v3.py
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
from openmdao.api import SqliteRecorder  # Recorder
import sqlitedict
from pprint import pprint

# PythonWrapper Components
class Parabola(Component):
    ''' Evaluates the equation f(x) = (x-3)^2 - 3 '''

    def __init__(self):
        super(Parabola, self).__init__()
        
        self.add_param('x', val=0.0)
        
        self.add_output('f_x', shape=1)
        
    def solve_nonlinear(self, params, unknowns, resids):
        ''' f(x) = (x-3)^2 - 3 '''
        
        x = params['x']
        
        unknowns['f_x'] = (x-3.0)**2 - 3.0

        
if __name__ == '__main__':

    # Instantiate a Problem 'sub'
    # Instantiate a Group and add it to sub
    sub = Problem()
    sub.root = Group()
    
    # Add the 'Parabola' Component to sub's root Group.
    sub.root.add('Parabola', Parabola())
    
    # Initialize x_init as a IndepVarComp and add it to sub's root group as 'p1.x_init'
    # p1.x_init is initialized to 2.0 because in OpenMETA, the metric 'x_i' (inside the Constants 'InitialValue') was connected to 'x_init'
    sub.root.add('p1', IndepVarComp('x_init', 2.0))  
    
    # Connect the IndepVarComp p1.x to Parabola.x
    sub.root.connect('p1.x_init', 'Parabola.x')
    
    # Add driver
    sub.driver = ScipyOptimizer()
    
    # Modify the optimization driver's settings
    sub.driver.options['optimizer'] = 'COBYLA'      # Type of Optimizer. 'COBYLA' does not require derivatives
    sub.driver.options['tol'] = 1.0e-4              # Tolerance for termination. Not sure exactly what it represents. Default: 1.0e-6
    sub.driver.options['maxiter'] = 200             # Maximum iterations. Default: 200
    #sub.driver.opt_settings['rhobeg'] = 1.0        # COBYLA-specific setting. Initial step size. Default: 1.0
    #sub.driver.opt_settings['catol'] = 0.1         # COBYLA-specific setting. Absolute tolerance for constraint violations. Default: 0.1
    
    # Add design variables, objective, and constraints to the optimization driver
    sub.driver.add_desvar('p1.x_init', lower=-50, upper=50)
    sub.driver.add_objective('Parabola.f_x')
    
    
    # Data collection
    recorder = SqliteRecorder('record_results')
    recorder.options['record_params'] = True
    recorder.options['record_metadata'] = True
    sub.driver.add_recorder(recorder)
    
    # Setup, run, & cleanupt
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