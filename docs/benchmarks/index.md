# Introduction to the benchmarks

## TODO

* [ ] What format should the benchmark data be stored in? 
    * Full fields? -> VMAP or scripting interfaces to solvers ([Abaqus scripting](https://classes.engineering.wustl.edu/2009/spring/mase5513/abaqus/docs/v6.5/books/cmd/default.htm?startat=pt02ch04s05.html), [PyAnsys postprocessing](https://post.docs.pyansys.com/version/stable/), [pybaqus](https://github.com/cristobaltapia/pybaqus/tree/master))
    * Only scalar values from sensors?
    * Ontology for benchmark results? [NFDI4Ing Metadata Profile service](https://profiles.nfdi4ing.de/#/editor)
* [ ] How do we deal with quadrature values like stresses?
    * Mapping to nodes? -> [Discussion on fenics forum](https://fenicsproject.discourse.group/t/comparative-analysis-ansys-vs-fenicsx-displacement-in-linear-elasticity/13398)
    * Can we export quadrature values and do the mapping ourselves?
* [ ] What is a good result?
    * Should we always do mesh-convergence? Cauchy series, if analytical solution is not known?
* [ ] Which element types? Linear, quadratic? underintegrated? 
* [ ] What is a sufficient format do describe an algorithm? 
    * Are algorithm boxes with noting more complicated than a matrix-vector product enough?
    * Do we always need a reference implementation?
* [x] Is it _easy_ to link a umat/usermat?
    * We think so. Both Abaqus and Ansys can link dynamically at runtime. You can also compile a new `ansys.exe`, but it is not required and mainly recommended for shipping the model.   