from ..interface import Problem, ProblemConfig
from .utils import create_dataset_directory_tree
import os
import torch
import numpy as np
from fenics import *
from mshr import *
import numpy as np
from itertools import product
from .utils import create_dataset_directory_tree, midpoints, get_param_space

set_log_active(False)

class NavierStokes2DCylinder(Problem):
    '''
    2D Navier-Stokes past a cylinder

    ...

    '''
    def __init__(self, config: ProblemConfig):
        super().__init__(config)

        self.directory = config.directory
        create_dataset_directory_tree(self.directory)
        self.save_vtk = config.save_vtk

        self.set_domain(config)

        self.parameters = config.parameters
        
        self.p1_space = get_param_space(self.parameters[0], config) #   mu: dynamic viscosity 
        self.p2_space = get_param_space(self.parameters[1], config) #   rho: density
        self.param_space = [self.p1_space, self.p2_space]
        self.param_instances = product(*self.param_space)

        self.Nh = self.mesh.num_vertices()    # number of DOF
        print(self.Nh)
        self.Nt = config.Nt                   # number of timesteps              
        self.Np = 3                           # num param + time
        self.N = len(sum(self.param_space,[]))

        self.time_interval = config.time_interval   
        self.dt = (self.time_interval[1]-self.time_interval[0]) / self.Nt 

        self.S = torch.empty(size=(self.N,self.Nt,self.Nh),dtype=torch.float32)
        self.P = torch.empty(size=(self.N,self.Nt,self.Np),dtype=torch.float32)


    def set_domain(self,config):
        if config.domain == 'rectangle':
            self.n = config.n
            channel = Rectangle(Point(0, 0), Point(2.2, 0.41))
            cylinder = Circle(Point(0.2, 0.2), 0.05)
            domain = channel - cylinder
            self.mesh = generate_mesh(domain, self.n)

            self.V = VectorFunctionSpace(self.mesh, 'P', 2)
            self.Q = FunctionSpace(self.mesh, 'P', 1)

            inflow   = 'near(x[0], 0)'
            outflow  = 'near(x[0], 2.2)'
            walls    = 'near(x[1], 0) || near(x[1], 0.41)'
            cylinder = 'on_boundary && x[0]>0.1 && x[0]<0.3 && x[1]>0.1 && x[1]<0.3'

            # Define inflow profile
            inflow_profile = ('4.0*1.5*x[1]*(0.41 - x[1]) / pow(0.41, 2)', '0')

            # Define boundary conditions
            bcu_inflow = DirichletBC(self.V, Expression(inflow_profile, degree=2), inflow)
            bcu_walls = DirichletBC(self.V, Constant((0, 0)), walls)
            bcu_cylinder = DirichletBC(self.V, Constant((0, 0)), cylinder)
            bcp_outflow = DirichletBC(self.Q, Constant(0), outflow)
            self.bcu = [bcu_inflow, bcu_walls, bcu_cylinder]
            self.bcp = [bcp_outflow]

            File(os.path.join(self.directory,'mesh/mesh.pvd')) << self.mesh
        else:
            raise SyntaxError('only rectangle is available as domain type')


    def solve(self):
        i=0
        for p1,p2 in self.param_instances:
            print('Solving for parameters instance #',i,' :', [p1,p2])

            if self.save_vtk:
                vtkfile = File(os.path.join(self.directory,'vtk','solution_'+str(i),'solution.pvd'))

            # Define trial and test functions
            u = TrialFunction(self.V)
            v = TestFunction(self.V)
            p = TrialFunction(self.Q)
            q = TestFunction(self.Q)

            # Define functions for solutions at previous and current time steps
            u_n = Function(self.V)
            u_  = Function(self.V)
            p_n = Function(self.Q)
            p_  = Function(self.Q)

            U  = 0.5*(u_n + u)
            n  = FacetNormal(self.mesh)
            f  = Constant((0, 0))
            k  = Constant(self.dt)
            mu = Constant(p1)
            rho = Constant(p2)

            # Define symmetric gradient
            def epsilon(u):
                return sym(nabla_grad(u))

            # Define stress tensor
            def sigma(u, p):
                return 2*mu*epsilon(u) - p*Identity(len(u))

            # Define variational problem for step 1
            F1 = rho*dot((u - u_n) / k, v)*dx + rho*dot(dot(u_n, nabla_grad(u_n)), v)*dx + inner(sigma(U, p_n), epsilon(v))*dx + dot(p_n*n, v)*ds - dot(mu*nabla_grad(U)*n, v)*ds - dot(f, v)*dx
            a1 = lhs(F1)
            L1 = rhs(F1)

            # Define variational problem for step 2
            a2 = dot(nabla_grad(p), nabla_grad(q))*dx
            L2 = dot(nabla_grad(p_n), nabla_grad(q))*dx - (1/k)*div(u_)*q*dx

            # Define variational problem for step 3
            a3 = dot(u, v)*dx
            L3 = dot(u_, v)*dx - k*dot(nabla_grad(p_ - p_n), v)*dx

            # Assemble matrices
            A1 = assemble(a1)
            A2 = assemble(a2)
            A3 = assemble(a3)

            # Apply boundary conditions to matrices
            [bc.apply(A1) for bc in self.bcu]
            [bc.apply(A2) for bc in self.bcp]

            # Time-stepping
            t = self.time_interval[0]

            for j in range(self.Nt):

                t += self.dt
                print('\tsolving for t=',t)
                # Step 1: Tentative velocity step
                b1 = assemble(L1)
                [bc.apply(b1) for bc in self.bcu]
                solve(A1, u_.vector(), b1, 'bicgstab', 'hypre_amg')

                # Step 2: Pressure correction step
                b2 = assemble(L2)
                [bc.apply(b2) for bc in self.bcp]
                solve(A2, p_.vector(), b2, 'bicgstab', 'hypre_amg')

                # Step 3: Velocity correction step
                b3 = assemble(L3)
                solve(A3, u_.vector(), b3, 'cg', 'sor')

                # ********** here you must stack sol vectors
                #self.S[i,j,:] = torch.from_numpy(u_.vector().get_local(vertex_to_dof_map(self.V)))
                #self.P[i,j,:] = torch.tensor([p1,p2,t])
                
                if self.save_vtk:
                    vtkfile << (u_, t)

                u_n.assign(u_)
                p_n.assign(p_)
            i+=1
            
    def save_dataset(self):
        torch.save(self.S, os.path.join(self.directory,'tensors/snapshots/S.pt'))
        torch.save(self.P, os.path.join(self.directory,'tensors/parameters/P.pt'))
        print('Dataset correctly saved to:', self.directory)
        