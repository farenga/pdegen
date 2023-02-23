from ..interface import Problem, ProblemConfig
from .utils import create_dataset_directory_tree
import os
import torch
import numpy as np
from fenics import *
from itertools import product
from .utils import create_dataset_directory_tree, midpoints, get_param_space

set_log_active(False)

class ADR2D(Problem):
    '''
    2D Advection-Diffusion-Reaction Equation:

    ...

    '''
    def __init__(self, config: ProblemConfig):
        super().__init__(config)

        self.directory = config.directory
        create_dataset_directory_tree(self.directory)
        self.save_vtk = config.save_vtk

        self.set_domain(config)

        self.parameters = config.parameters
        
        self.p1_space = get_param_space(self.parameters[0], config)
        self.p2_space = get_param_space(self.parameters[1], config)
        self.p3_space = get_param_space(self.parameters[2], config)
        self.p4_space = get_param_space(self.parameters[3], config)
        self.param_space = [self.p1_space, self.p2_space, self.p3_space, self.p4_space]
        self.param_instances = product(*self.param_space)

        self.Nh = self.mesh.num_vertices()    # number of DOF
        self.Nt = config.Nt                   # number of timesteps              
        self.Np = 5                           # num param + time
        self.N = len(sum(self.param_space,[]))

        self.time_interval = config.time_interval   # final time
        self.dt = (self.time_interval[1]-self.time_interval[0]) / self.Nt 

        self.S = torch.empty(size=(self.N,self.Nt,self.Nh),dtype=torch.float32)
        self.P = torch.empty(size=(self.N,self.Nt,self.Np),dtype=torch.float32)


    def set_domain(self,config):
        if config.domain == 'square':
            self.n = config.n
            self.mesh = RectangleMesh(Point(0, 0), Point(1, 1), self.n, self.n)
            self.V = FunctionSpace(self.mesh, 'P', 1)
            self.bc = DirichletBC(self.V, Constant(0), 'on_boundary')
            File(os.path.join(self.directory,'mesh/mesh.pvd')) << self.mesh
        else:
            raise SyntaxError('only square is available as domain type')


    def solve(self):
        i=0
        for p1,p2,p3,p4 in self.param_instances:
            print('Solving for parameters instance #',i,' :', [p1,p2,p3,p4])

            if self.save_vtk:
                vtkfile = File(os.path.join(self.directory,'vtk','solution_'+str(i),'solution.pvd'))

            # Define initial value
            u_0 = Constant(0.)
            u_n = interpolate(u_0, self.V)

            # Define variational problem
            u = TrialFunction(self.V)
            v = TestFunction(self.V)
            f = Expression("10.*exp(-(pow(x[0]-p3,2)+pow(x[1]-p4,2))/0.0049)", degree=2, p3=p3, p4=p4)
            b = Expression(("cos(2*pi*t/p2)","sin(2*pi*t/p2)"), degree=2, p2=p2, t=0)
            c = Constant(1.)
            a = u*v*dx + p1*self.dt*inner(grad(u),grad(v))*dx + self.dt*inner(b,grad(u))*v*dx + c*self.dt*u*v*dx
            L = u_n*v*dx + self.dt*f*v*dx

            # Time-stepping0
            u_sol = Function(self.V)
            t = self.time_interval[0]

            for j in range(self.Nt):

                t += self.dt
                solve(a == L, u_sol)

                self.S[i,j,:] = torch.from_numpy(u_sol.vector().get_local(vertex_to_dof_map(self.V)))
                self.P[i,j,:] = torch.tensor([p1,p2,p3,p4,t])
                
                if self.save_vtk:
                    vtkfile << (u_sol, t)

                u_n.assign(u_sol)
            i+=1
            
    def save_dataset(self):
        torch.save(self.S, os.path.join(self.directory,'tensors/snapshots/S.pt'))
        torch.save(self.P, os.path.join(self.directory,'tensors/parameters/P.pt'))
        print('Dataset correctly saved to:', self.directory)
        