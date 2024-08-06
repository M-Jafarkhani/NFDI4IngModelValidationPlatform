# Mises plasticity with linear isotropic hardening

A general plasticity model can be described by the following set of equations which are here taken from the Simo and Hughes book on computational inelasticity [@Simo1998](p. 83, BOX 2.1):

!!! note "General plasticity model[@Simo1998](p. 83, BOX 2.1)"
    1. Elastic stress-strain relationship:
    $$
    \boldsymbol{\sigma} = \mathbf C : (\boldsymbol{\varepsilon}-\boldsymbol{\varepsilon}_\mathrm{pl})
    $$
    2. Elastic domain in stress space
    $$
    \mathbb E_\sigma = \{(\boldsymbol{\sigma},\mathbf q)\in\mathbb S \times\mathbb R^m|f(\boldsymbol{\sigma},\mathbf q)\le 0\}.
    $$
    3. Flow rule and hardening law
        1. Non-associative case:
        $$
        \begin{aligned}
        \dot{\boldsymbol{\varepsilon}}_\mathrm{pl} &=\gamma\mathbf r(\boldsymbol{\sigma},\mathbf q)\\
        \dot{\mathbf q} &=-\gamma \mathbf h(\boldsymbol{\sigma},\mathbf q)\\
        \end{aligned}
        $$
        2. Associative case
        $$
        \begin{aligned}
        \dot{\boldsymbol{\varepsilon}}_\mathrm{pl} &=\gamma\frac{\partial f}{\partial \boldsymbol{\sigma}}\\
        \dot{\mathbf q} &=-\gamma \mathbf D\frac{\partial f}{\partial \mathbf q}\\
        \mathbf D &= \text{matrix of generalized plastic moduli}\\
        \end{aligned}
        $$
    4. Kuhn-Tucker loading/unloading conditions
    $$
    \gamma\ge 0,\;f(\boldsymbol{\sigma},\mathbf q)\le 0,\; \gamma f(\boldsymbol{\sigma},\mathbf q)=0
    $$
    5. Consistency condition
    $$
    \gamma \dot{f}(\boldsymbol{\sigma},\mathbf q)=0
    $$     