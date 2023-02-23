# PDEGen

PDEGen is an open-source package for generating datasets of time-dependent parameterized Partial Differential Equations (PDEs) solutions. 

The main aim of the library is to enable reproducibility in the field of Machine Learning for PDEs, where there is a lack of common benchmarking datasets, and dataset-sharing is usually unfeasible, due to file sizes.

Even though a kind of common ground for the typical benchmarking equations already exists (Burgers', Heat, Navier-Stokes), unreproducibility arises from additional variables that characterize the differential problems, such as parameters, forcing terms, domain shape and its discretization.

PDEGen tryies to solve those problems by providing an intuitive interface for datasets generation and reproduction, via simple configurations.


The library implements multiple standard problems (Heat, Advection-Diffusion-Reaction, Stokes)

## Install
    
    pip install pdegen

## Usage

    import pdegen
    pdegen.generate("problem_config.yaml")


### Configuration
