from ..interface import Problem, ProblemConfig
from .utils import create_dataset_directory_tree
import os
import torch
import numpy as np
from fenics import *
from itertools import product
from .utils import create_dataset_directory_tree, midpoints, get_param_space

set_log_active(False)

class Burgers1D(Problem):
    '''
    1D Burgers Equation:

    DuDt - Laplacian(u(x))=f(x), x in [-1,1]
    u(x) = uD(x)   , x on DOmega

    '''
    def __init__(self, config: ProblemConfig):
        super().__init__(config)

        self.directory = config.directory
        create_dataset_directory_tree(self.directory)

        self.save_vtk = config.save_vtk

        self.set_domain(config)

        self.parameters = config.parameters
        
        self.param_instances = get_param_space(self.parameters[0], config)

        self.Nh = self.mesh.num_vertices()    # number of DOF
        self.Nt = config.Nt                   # number of timesteps              
        self.Np = 2                           # num param + time
        self.N = len(self.param_instances)

        self.time_interval = config.time_interval   # final time
        self.dt = (self.time_interval[1]-self.time_interval[0]) / self.Nt 

        self.S = torch.empty(size=(self.N,self.Nt,self.Nh),dtype=torch.float32)
        self.P = torch.empty(size=(self.N,self.Nt,self.Np),dtype=torch.float32)


    def set_domain(self,config):
        if config.domain == 'unitinterval':
            self.n = config.n
            self.mesh = UnitIntervalMesh(self.n)
            self.V = FunctionSpace(self.mesh, 'P', 1)
            self.bc = DirichletBC(self.V, Constant(0), 'on_boundary')
            File(os.path.join(self.directory,'mesh/mesh.pvd')) << self.mesh
        else:
            raise SyntaxError('only unitinterval is available as domain type')


    def solve(self):
        for i,p1 in enumerate(self.param_instances):
            print('Solving for parameters instance #',i,' :', p1)

            if self.save_vtk:
                vtkfile = File(os.path.join(self.directory,'vtk','solution_'+str(i),'solution.pvd'))

            # Define initial value
            u_0 = Expression('-sin(2*pi*x[0])', degree=1)
            u_n = interpolate(u_0, self.V)

            # Define variational problem
            u = TrialFunction(self.V)
            v = TestFunction(self.V)
            f = Constant(0)

            F = ((u - u_n)/self.dt*v + u*u.dx(0)*v + p1*u.dx(0)*v.dx(0) )*dx

            # Time-stepping0
            u_sol = Function(self.V)
            F  = action(F, u_sol)
            t = self.time_interval[0]

            for j in range(self.Nt):

                t += self.dt
                solve(F==0, u_sol, self.bc)

                self.S[i,j,:] = torch.from_numpy(u_sol.vector().get_local(vertex_to_dof_map(self.V)))
                self.P[i,j,:] = torch.tensor([p1,t])
                
                if self.save_vtk:
                    vtkfile << (u_sol, t)

                u_n.assign(u_sol)

    def save_dataset(self):
        torch.save(self.S, os.path.join(self.directory,'tensors/snapshots/S.pt'))
        torch.save(self.P, os.path.join(self.directory,'tensors/parameters/P.pt'))
        print('Dataset correctly saved to:', self.directory)
        