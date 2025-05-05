# SCR-Benchmark-SCPR
This repository contains the results of **shape-constrained polynomial regression (SCPR)** on datasets of our shape-constrained regression benchmark [SCR-Benchmark](https://github.com/florianBachinger/SCR-Benchmarks-NIPS).


## Shape-constrained polynomial regression (SCPR)
The hyperparameters of SCPR are the total degree- $d$
of the polynomial, $\lambda$, to determine the strength of regularization, and $\alpha$ to
balance the 1-norm and the 2-norm penalties. We solve the semidefinite programming problem using the commercial solver [Mosek](https://www.mosek.com). Cf. [Hall](http://arks.princeton.edu/ark:/88435/dsp014m90dz20p) for a detailed
mathematical description of SCPR.
