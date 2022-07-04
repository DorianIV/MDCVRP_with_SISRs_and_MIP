To use either the Mixed integer Program or SISRs, use the solving.py file. One of the init methods
(init before everything except SISRS_1000_worse or init_worse_sol before SISRS_1000_worse) before
running any other methods. checking.txt can be used to manually check solutions, SISRs returns only
valid solutions, but when limiting the Mixed Integer Program in time, sometimes solutions are not
valid. Found improvements are stored in the Improvementes folder. NOTE: running an init with 
first_time=True will remove all stored solutions in this folder.

SISRS_1000(iterations) will run SIRSs on every instance using the solutions in the Instances folder.

SISRS_1000_worse(iterations) will run SISRs on every instance using the solutions in the 
After_Construction and After_Local_Search folder.

optimal_routes() will use CPLEX after removing one route at a time for every instance in the 
Instances folder.

combi_10(iterations) will use CPLEX in combination with the ruin-phase of SISRs to find improvements
on every instance in the instances folder.

model.two_routes(instance) will remove two routes every time and try to calculate the optimal 
solution using CPLEX. It will repeat this for every combination of two routes in an instance.