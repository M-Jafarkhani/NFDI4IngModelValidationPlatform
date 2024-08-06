# Linear elasticity

A general non-isotropic linear elastic material model consists of the follwoing equations:
!!! note "Linear elasticity equations"

    $$
    \begin{aligned}
    \boldsymbol{\varepsilon} &= \frac{1}{2}\left(\nabla \mathbf u +\nabla \mathbf u^\top\right)\\
    \boldsymbol{\sigma} &= \mathbf C : \boldsymbol{\varepsilon}
    \end{aligned}
    $$

!!! note "Linear elasticity equations -- incremental form"

    $$
    \begin{aligned}
    \Delta\boldsymbol{\varepsilon} &= \frac{1}{2}\left(\nabla \Delta\mathbf u +\nabla \Delta\mathbf u^\top\right)\\
    \Delta{\boldsymbol{\sigma}} &= \mathbf C : \Delta\boldsymbol{\varepsilon}
    \end{aligned}
    $$

