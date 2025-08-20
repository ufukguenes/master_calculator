# master_calculator
Shows you how to optimize your grade by moving subjects between different specialization modules.

### only for master grades in computer science

If I understood correctly, the grade for each sub-module (like specialization, elective studies, minor..) are rounded down and then the final grade of each sub-module is used in the weighted average (by ects per submodule) to calculate the final grade. This allows for some optimization by moving subjects into different sub-modules.

In the python script you can see how to use it (with my subjects, but random grades).

I implemented some checks, to see if the studies where picked correct, but not everything is checked (see below)

# THINGS THAT ARE NOT CHECKED!!!!
- if Stammodule where picked correctly
- Stammodule are NOT excluded from the amount of ects reagrding the required ects in lectures in the specialization, which is wrong
- when over 120 ects total, the module with the worst ects is cut off, I think, that is how it works, but it is ignored if the module would not meet the needed requirements without the cut off ects

# No guarantees that this is correct

Help is welcome, if you find a mistake,  let me know. 
