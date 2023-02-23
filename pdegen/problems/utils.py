import os
import numpy as np

def create_dataset_directory_tree(path: str):

    mesh_path = os.path.join(path,"mesh")
    tensors_path = os.path.join(path,"tensors")
    snapshots_path = os.path.join(tensors_path,"snapshots")
    params_path = os.path.join(tensors_path,"parameters")
    vtk_path = os.path.join(path,"vtk")

    makedir(path)
    makedir(mesh_path)
    makedir(tensors_path)
    makedir(snapshots_path)
    makedir(params_path)
    makedir(vtk_path)
    
    print('Dataset directory tree created')


def makedir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def midpoints(array: np.array):
    return (array[:-1] + array[1:])/2

def get_param_space(p, config):
    if len(p)==1:
        return p
    elif len(p)==3:
        p_space = np.linspace(p[0],p[1],p[2])
        if config.midpoints:
            p_space = midpoints(p_space)
        return p_space.tolist()
            
    else:
        raise ValueError('Input parameters must be a single valued array or a triple.')
