# Linear elasticity

## Tensor form
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

We first consider the special case of isotropic linear elasticity, where the tensor $\mathbf C$ is defined by the Lamé parameters $(\lambda,\mu)$ as

!!!note "Isotropic linear elasticity"
    $$
    \mathbf C = \lambda \mathbf 1 \otimes \mathbf 1 + 2\mu \mathbf I
    $$

with the second-order identity tensor $\mathbf 1=\delta_{ij}\boldsymbol{e}_i\otimes\boldsymbol{e}_j$, the fourth-order identity tensor $\mathbf I = \frac{1}{2}(\delta_{ik}\delta_{jl}+\delta_{il}\delta{jk})\boldsymbol{e}_i\otimes\boldsymbol{e}_j\otimes\boldsymbol{e}_k\otimes\boldsymbol{e}_l$ and the Kronecker Delta 
$$
\delta_{ij}=\begin{cases}1&,i=j\\0&,i\ne j\end{cases}.
$$

## Reduced Voigt/Mandel basis

The stress and strain are symmetric second-order $3\times 3$ tensors and can therefore be stored as a vector with dimension $6$. For example, the following map

$$
\begin{bmatrix}
   \sigma_{11} & \sigma_{12} &  \sigma_{13}  \\
   \sigma_{21} & \sigma_{22} &  \sigma_{23}  \\
   \sigma_{31} & \sigma_{32} &  \sigma_{33}  \\
   \end{bmatrix} \mapsto 
   \begin{bmatrix} \sigma_{11} \\
   \sigma_{22} \\
   \sigma_{33} \\
   \sigma_{12} \\
   \sigma_{13} \\
   \sigma_{23}
   \end{bmatrix}.
$$

would be sufficient. However, the shear components usually have eithr the factor 2 for the strains in Voigt-notation and th factor $\sqrt 2$ for the strains and stresses in Mandel notation:

!!! note "Voigt notation"
    $$
    \begin{aligned}
    \begin{bmatrix}
    \varepsilon_{11} & \varepsilon_{12} &  \varepsilon_{13}  \\
    \varepsilon_{21} & \varepsilon_{22} &  \varepsilon_{23}  \\
    \varepsilon_{31} & \varepsilon_{32} &  \varepsilon_{33}  \\
    \end{bmatrix} &\mapsto 
    \begin{bmatrix} \varepsilon_{11} &
    \varepsilon_{22} &
    \varepsilon_{33} &
    2\varepsilon_{12} &
    2\varepsilon_{13} &
    2\varepsilon_{23}
    \end{bmatrix}^\top\\
    \begin{bmatrix}
    \sigma_{11} & \sigma_{12} &  \sigma_{13}  \\
    \sigma_{21} & \sigma_{22} &  \sigma_{23}  \\
    \sigma_{31} & \sigma_{32} &  \sigma_{33}  \\
    \end{bmatrix} &\mapsto 
    \begin{bmatrix} \sigma_{11} &
    \sigma_{22} &
    \sigma_{33} &
    \sigma_{12} &
    \sigma_{13} &
    \sigma_{23}
    \end{bmatrix}^\top.
    \end{aligned}
    $$

!!! note "Mandel notation"
    $$
    \begin{aligned}
    \begin{bmatrix}
    \varepsilon_{11} & \varepsilon_{12} &  \varepsilon_{13}  \\
    \varepsilon_{21} & \varepsilon_{22} &  \varepsilon_{23}  \\
    \varepsilon_{31} & \varepsilon_{32} &  \varepsilon_{33}  \\
    \end{bmatrix} &\mapsto 
    \begin{bmatrix} \varepsilon_{11} &
    \varepsilon_{22} &
    \varepsilon_{33} &
    \sqrt 2\varepsilon_{12} &
    \sqrt 2\varepsilon_{13} &
    \sqrt 2\varepsilon_{23}
    \end{bmatrix}^\top\\
    \begin{bmatrix}
    \sigma_{11} & \sigma_{12} &  \sigma_{13}  \\
    \sigma_{21} & \sigma_{22} &  \sigma_{23}  \\
    \sigma_{31} & \sigma_{32} &  \sigma_{33}  \\
    \end{bmatrix} &\mapsto 
    \begin{bmatrix} \sigma_{11} &
    \sigma_{22} &
    \sigma_{33} &
    \sqrt 2\sigma_{12} &
    \sqrt 2\sigma_{13} &
    \sqrt 2\sigma_{23}
    \end{bmatrix}^\top.
    \end{aligned}
    $$

Mandel notation has the advantage that the inner product of two vectors, e.g. $\boldsymbol{\sigma}^\top\cdot\boldsymbol{\sigma}$ is the same as the inner product of its corresponding symmetric tensor $\boldsymbol{\sigma}:\boldsymbol{\sigma}$. Therefore, we will investigate Mandel form. The isotropic elasticity tensor converts to

!!! note "Elasticity tensor -- Mandel form"
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
    **Remark:** In Voigt-Notation, the $(4,4)$-th, the $(5,5)$-th and the $(6,6)$-th component are $\mu$ instead of $2\mu$. Therefore, the translation from tensor to Mandel-notation is considered to be more intuitive.

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


