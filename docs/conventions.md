# Conventions and notation

## Gradients of vector fields

The gradient of a vector field $\phi$ with

$$
\begin{aligned}
\phi:\mathbb R^n &\to \mathbb R^n\\
x&\mapsto \phi(x)
\end{aligned}
$$

is defined as 

$$
\nabla \phi = \frac{\partial\phi_i}{\partial x_j}\mathbf e_i\otimes\mathbf e_j.
$$

!!! note
    Some sources define the gradient of a vector field with $\partial\phi_j/\partial x_i$ for the $ij$-th component of the matrix.

## Mandel notation

The basis of symmetric $3\times3$ tensors is not

$$
\left\{ \begin{bmatrix}1 & 0 & 0\\
0 & 0 & 0\\
0 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 0\\
0 & 1 & 0\\
0 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 0\\
0 & 0 & 0\\
0 & 0 & 1
\end{bmatrix},\begin{bmatrix}0 & 1 & 0\\
1 & 0 & 0\\
0 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 1\\
0 & 0 & 0\\
1 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 0\\
0 & 0 & 1\\
0 & 1 & 0
\end{bmatrix}\right\} 
$$

because the elements are not normed, therefore

$$
\begin{aligned}
B^{t}  =&\left\{ \begin{bmatrix}1 & 0 & 0\\
0 & 0 & 0\\
0 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 0\\
0 & 1 & 0\\
0 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 0\\
0 & 0 & 0\\
0 & 0 & 1
\end{bmatrix},\right.\\
&\left.\begin{bmatrix}0 & \frac{1}{\sqrt{2}} & 0\\
\frac{1}{\sqrt{2}} & 0 & 0\\
0 & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & \frac{1}{\sqrt{2}}\\
0 & 0 & 0\\
\frac{1}{\sqrt{2}} & 0 & 0
\end{bmatrix},\begin{bmatrix}0 & 0 & 0\\
0 & 0 & \frac{1}{\sqrt{2}}\\
0 & \frac{1}{\sqrt{2}} & 0
\end{bmatrix}\right\} \\
 & =\left\{ B_{1},\ldots,B_{6}\right\} 
\end{aligned}
$$

is an orthonormal basis of symmetric tensors with $B_{i}:B_{j}=\delta_{ij}$.
An orthonormal basis of a reduced vector notation similar to Voigt
notation is

$$
\begin{aligned}
B^{v} & =\left\{ \begin{bmatrix}1\\
0\\
\vdots\\
0
\end{bmatrix},\ldots,\begin{bmatrix}0\\
\vdots\\
0\\
1
\end{bmatrix}\right\} \\
 & =\left\{ e_{1},\ldots,e{}_{6}\right\} .
\end{aligned}
$$

A symmetric tensor can be written as the sum

$$
w^{t}=\sum_{i=1}^{6}\alpha_{i}B_{i}.
$$

A straightforward way to transform $w^{t}$ to a reduced vector representation
$w^{v}$ would be to write $w^{v}$ as

$$
w^{v}=\sum_{i=1}^{6}\alpha_{i}e_{i},
$$

thereby keeping the scalars $\alpha_{i}$ in the representation. Let
us consider a strain tensor $\boldsymbol{\varepsilon}$ which is decomposed
as

$$
\begin{aligned}
\begin{bmatrix}\varepsilon_{11} & \varepsilon_{12} & \varepsilon_{13}\\
\varepsilon_{12} & \varepsilon_{22} & \varepsilon_{23}\\
\varepsilon_{13} & \varepsilon_{23} & \varepsilon_{33}
\end{bmatrix}= & \varepsilon_{11}\begin{bmatrix}1 & 0 & 0\\
0 & 0 & 0\\
0 & 0 & 0
\end{bmatrix}+\varepsilon_{22}\begin{bmatrix}0 & 0 & 0\\
0 & 1 & 0\\
0 & 0 & 0
\end{bmatrix}+\varepsilon_{33}\begin{bmatrix}0 & 0 & 0\\
0 & 0 & 0\\
0 & 0 & 1
\end{bmatrix}\\
 & +\sqrt{2}\varepsilon_{12}\begin{bmatrix}0 & \frac{1}{\sqrt{2}} & 0\\
\frac{1}{\sqrt{2}} & 0 & 0\\
0 & 0 & 0
\end{bmatrix}+\sqrt{2}\varepsilon_{13}\begin{bmatrix}0 & 0 & \frac{1}{\sqrt{2}}\\
0 & 0 & 0\\
\frac{1}{\sqrt{2}} & 0 & 0
\end{bmatrix}+\sqrt{2}\varepsilon_{23}\begin{bmatrix}0 & 0 & 0\\
0 & 0 & \frac{1}{\sqrt{2}}\\
0 & \frac{1}{\sqrt{2}} & 0
\end{bmatrix}.
\end{aligned}
$$

Due to the components of value $\frac{1}{\sqrt{2}}$ in the basis,
the shear components of the strain get the factor $\sqrt{2}$. In
the vector representation, this leads to 

$$
\boldsymbol{\varepsilon}=\varepsilon_{11}\begin{bmatrix}1\\
0\\
0\\
0\\
0\\
0
\end{bmatrix}+\varepsilon_{22}\begin{bmatrix}0\\
1\\
0\\
0\\
0\\
0
\end{bmatrix}+\varepsilon_{33}\begin{bmatrix}0\\
0\\
1\\
0\\
0\\
0
\end{bmatrix}+\sqrt{2}\varepsilon_{12}\begin{bmatrix}0\\
0\\
0\\
1\\
0\\
0
\end{bmatrix}+\sqrt{2}\varepsilon_{13}\begin{bmatrix}0\\
0\\
0\\
0\\
1\\
0
\end{bmatrix}+\sqrt{2}\varepsilon_{23}\begin{bmatrix}0\\
0\\
0\\
0\\
0\\
1
\end{bmatrix}=\begin{bmatrix}\varepsilon_{11}\\
\varepsilon_{22}\\
\varepsilon_{33}\\
\sqrt{2}\varepsilon_{12}\\
\sqrt{2}\varepsilon_{13}\\
\sqrt{2}\varepsilon_{23}
\end{bmatrix},
$$

which is known as the Mandel form. Since the Mandel form maps an orthonormal
basis to an orthonormal basis -- something, the Voigt form does not
do -- some important properties as preserved. 

### Inner product is preserved

The inner product of two symmetric tensors $f^{t},g^{t}$ is 

$$
\begin{aligned}
f^{t}:g^{t} & =\left(\sum_{i=1}^{6}\alpha_{i}B_{i}\right):\left(\sum_{j=1}^{6}\beta_{j}B_{j}\right)\\
 & =\sum_{i,j=1}^{6}\alpha_{i}\beta_{j}\underbrace{B_{i}:B_{j}}_{=\delta_{ij}}\\
 & =\sum_{i=1}^{6}\alpha_{i}\beta_{i},
\end{aligned}
$$

and similarly

$$
\begin{aligned}
f^{v}\cdot g^{v} & =\left(\sum_{i=1}^{6}\alpha_{i}e_{i}\right)\cdot\left(\sum_{j=1}^{6}\beta_{j}e_{j}\right)\\
 & =\sum_{i,j=1}^{6}\alpha_{i}\beta_{j}\underbrace{e_{i}\cdot e_{j}}_{=\delta_{ij}}\\
 & =\sum_{i=1}^{6}\alpha_{i}\beta_{i}.
\end{aligned}
$$

This means that inner products of a strain with a stress, a stress
with a stress or a strain with a strain yield the same result in tensor-
and in Mandel notation. No scaling matrices as in the Voigt notation
are required.

### Properties of outer product are preserved

The outer product of two symmetric tensors is a linear map which maps
second order tensors to second order tensors. Let $f^{t},g^{t},h^{t}$
be symmetrical tensors, then

$$
\begin{aligned}
\left(f^{t}\otimes g^{t}\right):h^{t} & =\left(\sum_{i,j=1}^{6}\alpha_{i}\beta_{j}B_{i}\otimes B_{j}\right):\sum_{k=1}^{6}\gamma_{k}B_{k}\\
 & =\sum_{i,j,k=1}^{6}\alpha_{i}\beta_{j}\gamma_{k}B_{i}\otimes\underbrace{B_{j}:B_{k}}_{=\delta_{jk}}\\
 & =\sum_{i,j=1}^{6}\alpha_{i}\beta_{j}\gamma_{j}B_{i},
\end{aligned}
$$

and for the Mandel notation

$$
\begin{aligned}
\left(f^{v}\left(g^{v}\right)^{\top}\right)\cdot h^{t} & =\left(\sum_{i,j=1}^{6}\alpha_{i}\beta_{j}e_{i}e_{j}^{\top}\right)\cdot\sum_{k=1}^{6}\gamma_{k}e_{k}\\
 & =\sum_{i,j,k=1}^{6}\alpha_{i}\beta_{j}\gamma_{k}e_{i}\underbrace{e_{j}^{\top}e_{k}}_{=\delta_{jk}}\\
 & =\sum_{i,j=1}^{6}\alpha_{i}\beta_{j}\gamma_{j}e_{i}.
\end{aligned}
$$

Therefore, all outer products of symmetrical tensors have the same
meaning as they do in Mandel form when they are used as a map on symmetrical
tensors.