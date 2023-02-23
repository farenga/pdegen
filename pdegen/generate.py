from .interface import ProblemConfig, parse_config
from .problems import Heat2D

PROBLEMS_DICT = {
    'heat2d': Heat2D,
    }

def generate(config: ProblemConfig or str):
    
    if type(config) is str:
        config = parse_config(config)

    problem = PROBLEMS_DICT[config.problem](config)
    problem.solve()
    problem.save_dataset()
