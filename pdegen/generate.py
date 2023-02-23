from .interface import ProblemConfig, parse_config
from .problems import *

PROBLEMS_DICT = {
    'burgers1d': Burgers1D,
    'heat2d': Heat2D,
    'adr2d': ADR2D
    }

def generate(config: ProblemConfig or str):
    
    if type(config) is str:
        config = parse_config(config)

    problem = PROBLEMS_DICT[config.problem](config)
    problem.solve()
    problem.save_dataset()
