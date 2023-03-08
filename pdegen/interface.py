import os
import h5py
from dataclasses import dataclass
import yaml

@dataclass
class ProblemConfig:

    problem: str
    domain: str
    parameters: int or list         # Parameters [a,b,...] or [[a0,a1,Na],[b0,b1,Nb]]
    midpoints: bool = False         # Take the midpoints of the specified parameters spaces
    n: int = 128                    # Number of lateral dof
    Nt: int = None                  # Number of timesteps
    time_interval: list = None      # Time interval [t0,t1]
    directory: str = ''             # Path to working directory
    filename: str = 'dataset'       # Dataset name
    save_vtk: bool = False          # Save vtk .pvd visualization files
    save_mesh: bool = False         # Save mesh .pvd file

class Problem:
    def __init__(self, config: ProblemConfig or str):
        pass
    
    def solve(self):
        pass
    
    def save_dataset(self):
        h5_file = h5py.File(os.path.join(self.directory,self.filename+'.hdf5'), 'w')
        h5_file.create_dataset('S', data=self.S)
        h5_file.create_dataset('P', data=self.P)
        h5_file.create_dataset('coords', data=self.coords)
        h5_file.close()
        print('Dataset correctly saved to:', self.directory)

def parse_config(filepath):
    
    with open(filepath, 'r') as stream:
        config_file = yaml.safe_load(stream)

    problem_config = ProblemConfig(
        problem = config_file['problem'],
        domain = config_file['domain'],
        parameters = config_file['parameters'],
        midpoints= config_file['midpoints'],
        n = config_file['n'],
        Nt = config_file['Nt'],
        time_interval=config_file['time_interval'],
        directory = config_file['directory'],
        filename = config_file['filename'],
        save_mesh = config_file['save_mesh']
        save_vtk = config_file['save_vtk']
    )

    return problem_config
            
