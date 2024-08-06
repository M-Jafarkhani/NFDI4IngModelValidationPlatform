# Welcome the NFDI4Ing Model Validation Platform

This platform aims to validate implementations of mechanical constitutive models.

## Current goals (Wonderpill)

1. Create a generalized interface design for user-defined material model (e.g. UMATs in Abaqus) such that
    1. you can easily convert a constitutive model from any commercial or non-commercial FEM solver to this interface such that interoperability between solvers is possible,
    2. the implemented models can be any small-strain, large-deformation model.
2. Establish a comprehensive set of numerical benchmarks for:
    1. Linear elasticity
        * Critical factors include element order, mapping stresses to nodes, combined rotation and stretch
    2. Mises plasticity with linear isotropinc hardening
        * Critical factors include loading, unloading, reloading
    3. Dynamic test case for linear elasticity (some form of wave propagation)
3. Parts of the platform
    1. A website for the visualization of benchmark results in the form of interactive jupyter notebooks
    2. GitHub repository with the validation workflows
    3. Excecution platform for the workflows (optional goal because of licensing issues)
    4. Database platform for benchmark results