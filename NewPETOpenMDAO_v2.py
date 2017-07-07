'''
# Name: NewPETOpenMDAO_v1.py
# Company: MetaMorph, Inc.
# Author(s): Joseph Coombe
# Email: jcoombe@metamorphsoftware.com
# Create Date: 7/7/2017
# Edit Date: 7/7/2017

# Tutorial: Simple optimization of a paraboloid encapsulated within a SubProblem in OpenMDAO
#           Adaption of OpenMDAO tutorial: http://openmdao.readthedocs.io/en/1.7.3/usr-guide/tutorials/paraboloid-tutorial.html

# Inputs:

# Outputs:
'''

from __future__ import print_function
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer  # Optimizer driver
from openmdao.api import FullFactorialDriver  # FullFactorialDriver driver
from openmdao.api import ExecComp  # 'Quick Component' - useful for creating constraints
from openmdao.api import SubProblem  # Allows for nested drivers - not currently supported in OpenMETA - Introduced in OpenMDAO v.1.7.2.
from openmdao.api import SqliteRecorder  # Recorder
import sqlitedict  
from pprint import pprint

# First, let's create the component defining our system. We'll call it 'Paraboloid'.
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
        
class Sub(Problem):
    def __init__(self):
        super(Sub, self).__init__()
        
        self.root = Group()
        
        # Add the 'Paraboloid Component' to sub's root Group. Alternatively, I could have placed the 'Paraboloid' Component within a group
        self.root.add('P', Paraboloid())
        
        # Initialize x and y values in seperate IndepVarComps and add them to sub's root group
        self.root.add('p1', IndepVarComp('x', 13.0))
        self.root.add('p2', IndepVarComp('y', -14.0))
        
        # Define a constraint equation and add it to top's root Group
        self.root.add('con', ExecComp('c = x - y'))
        
        # Connect 'p1.x' and 'p2.y' to 'con.x' and 'con.y' respectively
        self.root.connect('p1.x', 'con.x')
        self.root.connect('p2.y', 'con.y')
        
        # Connect the IndepVarComps 'p1.x' and 'p2.y' to 'T.Paraboloid.x' and 'T.Paraboloid.y' respectively
        self.root.connect('p1.x', 'P.x')
        self.root.connect('p2.y', 'P.y')

        # Instantiate sub's optimization driver
        self.driver = ScipyOptimizer()
        
        # Modify the optimization driver's settings
        self.driver.options['optimizer'] = 'COBYLA'  # Type of Optimizer. 'COBYLA' does not require derivatives
        self.driver.options['tol'] = 1.0e-4  # Tolerance for termination. Not sure exactly what it represents. Default: 1.0e-6
        self.driver.options['maxiter'] = 200  # Maximum iterations. Default: 200
        self.driver.opt_settings['rhobeg'] = 1.0  # Initial step size. Default: 1.0
        #sub.driver.opt_settings['catol'] = 0.1  # Absolute tolerance for constraint violations
        
        # Add design variables, objective, and constraints to the optimization driver
        self.driver.add_desvar('p1.x', lower=-50, upper=50)
        self.driver.add_objective('P.f_xy')
        self.driver.add_constraint('con.c', lower=15.0)
        self.driver.add_constraint('p1.x', lower=-50.0, upper=50.0)  # Note adding this while this variable constraint reduces the degree to which
                                                                    # the constraint is violated, it does not eliminate the violation
        # ^ Jonathan comments that you often have to add constraints for the design variable ranges since the design variable bounds
        # are either not passed along to SciPy or are not enforced.    
        
if __name__ == '__main__':

    
    # Instantiate a top-level Problem 'top'
    # Instantiate a Group and add it to sub
    top = Problem()
    top.root = Group()
    
    # Initialize y as IndepVarComp and add it to top's root group
    top.root.add('p2', IndepVarComp('y', -14.0)) 
    
    # Add Problem 'sub' to 'top' as a SubProblem
    top.root.add('subprob', SubProblem(Sub(), params=['p2.y'],
                                            unknowns=['P.f_xy']))  # This is where you designate what to expose to the outside world
    
    # Connect top's IndepVarComps to SubProblem's params
    top.root.connect('p2.y', 'subprob.p2.y')
    
    # Add driver
    top.driver = FullFactorialDriver(num_levels=20)
    
    # Add design variables, objective, and constraints
    top.driver.add_desvar('p2.y', lower=-50, upper=50)

    # Data collection
    recorder = SqliteRecorder('record_results')
    recorder.options['record_params'] = True
    recorder.options['record_metadata'] = True
    top.driver.add_recorder(recorder)
    
    # Setup
    top.setup(check=False)
    
    # Run 
    top.run()
    
    # Cleanup
    top.cleanup()
    
    # Data retrieval & display
    # Old way - good for debugging IndepVars
    db = sqlitedict.SqliteDict( 'record_results', 'iterations' )
    db_keys = list( db.keys() ) # list() needed for compatibility with Python 3. Not needed for Python 2
    for i in db_keys:
        data = db[i]
        print('\n')
        print(data['Unknowns'])
        print(data['Parameters'])