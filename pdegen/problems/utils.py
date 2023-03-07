import os
import numpy as np
from vtk import vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy

def create_dataset_directory_tree(directory_path: str,save_vtk: bool=False, save_mesh: bool=False):
    makedir(directory_path)
    if save_vtk:
        vtk_path = os.path.join(directory_path,"vtk")
        makedir(vtk_path)
    if save_mesh:
        mesh_path = os.path.join(directory_path,"mesh")
        makedir(mesh_path)
    print('Dataset directory tree created.')


def makedir(directory_path):
    if not os.path.isdir(directory_path):
        os.makedirs(directory_path)


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


def load_mesh_coords(mesh_path: str, return_split: bool=False):
        reader = vtkXMLUnstructuredGridReader()
        reader.SetFileName(mesh_path)
        reader.Update()  
        nodes_vtk_array= reader.GetOutput().GetPoints().GetData()
        nodes_numpy_array = vtk_to_numpy(nodes_vtk_array)

        if return_split:
            return nodes_numpy_array[:,0] , nodes_numpy_array[:,1]
        else:
            return nodes_numpy_array
    
