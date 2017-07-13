# PET Buildup - Connecting Design Variables/Problem Inputs to Problem Outputs
Incremental buildup of a PET in OpenMETA along with its intended OpenMDAO behavior.

This example focuses on our proposed solution to a specific Problem that we encountered in OpenMDAO when trying to connect Problem Inputs to Problem Outputs.

Suppose, inside your 'Vahana' PET, you have a sub-PET 'Optimize' that minimizes total energy use 'E' by optimizing the propeller radius 'rProp'. The 'Vahana' 
PET also has a Component 'CalculateCost' that takes in two Parameters 'E' and 'rProp' in order to calculate the estimated trip cost 'C'.

Now, there is no problem if inside 'Optimize' the Design Variable 'rProp' is not connected to a Problem Input. You can simply connect
the Optimizer's Design Variable 'rProp' to a Problem Output within 'Optimize' and `run_mdao` will add the IndepVarComp associated with 'rProp'
to the SubProblem constructor's list of unknowns (`Vahana.root.add('Optimize', SubProblem('Optimize', params=[], unknowns=['p1.rProp' , '... .E']))).

However, there is a problem if the Design Variable 'rProp' is connected to a 'Problem Input' inside 'Optimize' since Problem Inputs
are also exposed in the SubProblem constructor. If you connect the Problem Input 'rProp' to a Problem Output, `run_mdao` will add the IndepVarComp
associated with 'rProp' to both the SubProblem constructor's list of unknowns and params (`Vahana.root.add('Optimize', SubProblem('Optimize', 
params=['p1.rProp'], unknowns=['p1.rProp' , '... .E']))). Then `open_mdao` will give you an error when it tries to connect `Optimize.p1.rProp` to 
`CalculateCost.rProp` - `Target 'CalculateCost.rProp' is connected to multiple unknowns: ['Optimize.p1.rProp', 'p1.rProp']`

In OpenMDAO, if you have three Components `foo`, `bar`, and `baz` - each with an input `x` and an output `z` - and you make the following connect statements:
`prob.root.connect('foo.z', 'bar.x')`
`prob.root.connect('bar.x', 'baz.x')`
OpenMDAO will effectively make the following connections:
`prob.root.connect('foo.z', 'bar.x')`
`prob.root.connect('foo.z', 'baz.x')`

Our workaround is to have `run_mdao` create a ExecComp (`Optimize.add('output', ExecComp('rProp = input'))`) for every Problem Input connected to a Problem 
Output within a PET, connect the Problem Input's associated IndepVarComp to the ExecComp (`Optimize.connect('Optimize.p1.rProp', 'output.input')`), and
and add that ExecComp's output to the SubProblem constructor's list of unknowns (`Vahana.root.add('Optimize', SubProblem('Optimize', params=['p1.rProp'], 
unknowns=['output.rProp' , '... .E']))`). This is pretty hacky so if anyone has a better idea, I'm all ears.

*Under Construction*
---
### OpenMETA PET ...
![sub](images/sub_v1.PNG)

### OpenMDAO interpretation
```python

```
#### Results:  
Run ``

---