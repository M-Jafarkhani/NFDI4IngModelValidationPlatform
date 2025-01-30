# Linear elasticity

## Tensor form
A general non-isotropic linear elastic material model consists of the follwoing equations:

$$
\begin{aligned}
\boldsymbol{\varepsilon} &= \frac{1}{2}\left(\nabla \mathbf u +\nabla \mathbf u^\top\right)\\
\boldsymbol{\sigma} &= \mathbf C : \boldsymbol{\varepsilon}
\end{aligned}
$$


We first consider the special case of isotropic linear elasticity, where the tensor $\mathbf C$ is defined by the Lamé parameters $(\lambda,\mu)$ as


$$
\mathbf C = \lambda \mathbf 1 \otimes \mathbf 1 + 2\mu \mathbf I
$$

with the second-order identity tensor $\mathbf 1=\delta_{ij}\boldsymbol{e}_i\otimes\boldsymbol{e}_j$, the fourth-order identity tensor $\mathbf I = \frac{1}{2}(\delta_{ik}\delta_{jl}+\delta_{il}\delta{jk})\boldsymbol{e}_i\otimes\boldsymbol{e}_j\otimes\boldsymbol{e}_k\otimes\boldsymbol{e}_l$ and the Kronecker Delta 
$$
\delta_{ij}=\begin{cases}1&,i=j\\0&,i\ne j\end{cases}.
$$

## Reduced Voigt/Mandel basis

As shown in the conventions section, the Mandel form is a reduced notation of symmetrical tensors that preserves inner products and some properties of the outer product. The elasticity tensor in Mandel form is therefor trivially determined by the Lamé parameters $(\lambda,\mu)$ as


$$
\mathbf C = 2\mu\mathbf I_6 + \lambda \mathbf 1 \otimes \mathbf 1
$$
with $\mathbf 1=[1,1,1,0,0,0]$ being the representation of the second-order identity in Mandel form and the identity matrix $\mathbf I_6$ which maps the strain in mandel form to itself, as does the fourth-order identity to the tensor representation of the strain.
$$
\mathbf C = \begin{bmatrix}
2\mu+\lambda & \lambda & \lambda & 0 & 0 & 0 \\
\lambda & 2\mu+\lambda & \lambda & 0 & 0 & 0 \\
\lambda & \lambda & 2\mu+\lambda & 0 & 0 & 0 \\
0 & 0 & 0 & 2\mu & 0 & 0 \\
0 & 0 & 0 & 0 & 2\mu & 0 \\
0 & 0 & 0 & 0 & 0 & 2\mu \end{bmatrix}
$$

**Remark:** In Voigt-Notation, the $(4,4)$-th, the $(5,5)$-th and the $(6,6)$-th component are $\mu$ instead of $2\mu$. 

## Algorithm

!!! note "Algorithm: Linear elasticity -- incremental formulation"
    **Parameters:** $\lambda,\mu$

    **Input:** $\boldsymbol{\sigma}^n,\Delta\boldsymbol{\varepsilon}^n$ in Mandel notation

    **Output:** $\boldsymbol{\sigma}^{n+1}$ in Mandel Notation

    $$
    \mathbf C = \begin{bmatrix}
    2\mu+\lambda & \lambda & \lambda & 0 & 0 & 0 \\
    \lambda & 2\mu+\lambda & \lambda & 0 & 0 & 0 \\
    \lambda & \lambda & 2\mu+\lambda & 0 & 0 & 0 \\
    0 & 0 & 0 & 2\mu & 0 & 0 \\
    0 & 0 & 0 & 0 & 2\mu & 0 \\
    0 & 0 & 0 & 0 & 0 & 2\mu \end{bmatrix}
    $$
    $$
    \boldsymbol{\sigma}^{n+1}=\boldsymbol{\sigma}^n+\mathbf C \cdot \Delta\boldsymbol{\varepsilon}^n
    $$


