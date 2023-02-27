from .interface import ProblemConfig, parse_config
from .problems import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--config', type=str, default=None, help='Path to the yaml config file')
   
PROBLEMS_DICT = {
    'burgers1d': Burgers1D,
    'heat2d': Heat2D,
    'adr2d': ADR2D,
    'navierstokes2d': NavierStokes2DCylinder
    }

def generate(config: ProblemConfig or str):
    
    if type(config) is str:
        config = parse_config(config)

    problem = PROBLEMS_DICT[config.problem](config)
    problem.solve()
    problem.save_dataset()


if __name__ == "__main__":
    args = parser.parse_args()
    generate(args.config)