# PDEGen
<p align="center">
<img align="middle" src="./assets/heat.png" alt="dataset tensor" width="500" />
</p>

PDEGen is an open-source package for generating datasets of time-dependent parameterized Partial Differential Equations (PDEs) solutions. 

The main aim of the library is to enable reproducibility in the field of Data-Driven PDEs modeling, whose benchmarking datasets landscape is usually characterized by:
- low data availability/sharing
- data fragmentation (snapshots, parameters, meshes)
- heavy non-tensorized data formats

PDEGen aims to enable datasets generation and reproduction via pre-implemented pde-solvers scripts and a common configuration files-based interface.

In such a way sharing the configuration file is enough for setting up the problem and generating data, instead of sharing big and fragmented datasets.

## Install
    
    pip install pdegen

## Usage
### CLI

    python3 -m pdegen.generate --config examples/ns2d.yaml 

### Script
By loading a configuration .yaml file

    import pdegen
    pdegen.generate("examples/ns2d.yaml")

or by via ProblemConfig class

    from pdegen import ProblemConfig

    problem_config = ProblemConfig(
        problem = 'heat2d',
        ...
    )
    
    pdegen.generate(problem_config)

## Dataset structure

The generated dataset has the following structure:

    dataset/
        ├── tensors/
        |      ├── snapshots/
        |      |     ├── S.pt
        |      |     └── ...
        |      └── parameters/
        |            ├── P.pt
        |            └── ...
        ├── mesh/
        │      └── mesh.pvd
        └── vtk/...

With the following tensors shapes:

- S: (N,Nt,Nh)
- P: (N,Nt,Np)

where:
- N: number of parameters instances
- Nt: number of timesteps
- Nh: number of spatial dop
- Np: number of models' parameters + 1 (including time)