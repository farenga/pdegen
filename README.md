# PDEGen
<p align="center">
<img align="middle" src="./assets/heat.png" alt="dataset tensor" width="500" />
</p>

PDEGen is an open-source package for generating datasets of time-dependent parameterized Partial Differential Equations (PDEs) solutions. 

The main aim of the library is to enable reproducibility in the field of Data-Driven PDEs modeling, whose benchmarking datasets landscape is usually characterized by:
- low data availability/sharing
- data fragmentation (snapshots, parameters, meshes)
- Heavy non-tensorized data formats

PDEGen aims to enable datasets generation and reproduction via pre-implemented pde-solvers scripts and a common configuration files-based interface.

In such a way sharing the configuration file is enough for setting up the problem and generating data, instead of sharing big and fragmented datasets.

## Install
    
    pip install git+https://github.com/farenga/pdegen

## Usage
By loading a YAML configuration file:

    import pdegen
    pdegen.generate("problem_config.yaml")

or by defining a ProblemConfig

    from pdegen import ProblemConfig

    problem_config = ProblemConfig(
        problem = 'heat2d',
        ...
    )
    
    pdegen.generate("problem_config.yaml")