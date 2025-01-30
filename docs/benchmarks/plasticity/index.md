# Mises plasticity with isotropic and kinematic hardening hardening

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

 For plasticity with isotropic and kinematic hardening, the history variables are defined as $\mathbf q=\{\alpha,\bar{\boldsymbol{\beta}\}}$, with the equivalent plastic strain $\alpha$ and the back stress $\bar{\boldsymbol{\beta}}$. The yield condition, flow rule and hardening law are given by:

!!! note "Von Mises yield condition with isotropic and kinematic hardening"
    $$
    \begin{aligned}
    \boldsymbol{\eta} &= \mathrm{dev}(\boldsymbol{\sigma})-\bar{\boldsymbol{\beta}}, \quad \mathrm{tr}(\bar{\boldsymbol{\beta}})=0\\
    f(\boldsymbol{\sigma},\alpha,\bar\beta) &= \Vert\boldsymbol{\eta}\Vert_2-\sqrt{\frac{2}{3}}K(\alpha)\\
    \dot{\boldsymbol{\varepsilon}}_\mathrm{pl} &= \gamma\frac{\boldsymbol{\eta}}{\Vert\boldsymbol{\eta}\Vert_2} \\
    \dot{\bar{\boldsymbol{\beta}}} &= \gamma \frac{2}{3}H'(\alpha)\frac{\boldsymbol{\eta}}{\Vert\boldsymbol{\eta}\Vert_2} \\
    \dot{\alpha} &= \gamma\sqrt{\frac{2}{3}}\\
    \end{aligned}
    $$

With $\mathbf n = \frac{\boldsymbol{\eta}}{\Vert \boldsymbol{\eta}\Vert_2}$, elastoplastic tangent is given by:
    $$
    \mathbf C = \kappa \mathbf 1\otimes\mathbf 1 + 2\mu\left(\mathbf I -\frac{1}{3}\mathbf 1\otimes \mathbf 1 - \frac{\mathbf n \otimes \mathbf n}{1+\frac{H'+K'}{3\mu}}\right)
    $$

## Mises plasticity with linear isotropic hardening

The isotropic hardening function is defined as $K(\alpha) = \sigma_0 + H\alpha$, where $\sigma_0$ is the initial yield stress, $H$ is the hardening modulus and $\alpha$ is the equivalent plastic strain. The elastoplastic tangent is given by:
    $$
    \mathbf C = \kappa \mathbf 1\otimes\mathbf 1 + 2\mu\left(\mathbf I -\frac{1}{3}\mathbf 1\otimes \mathbf 1 - \frac{\mathbf n \otimes \mathbf n}{1+\frac{H}{3\mu}}\right)
    $$