import argparse

from .generate import generate

parser = argparse.ArgumentParser()
parser.add_argument('config', type=str, default=None, help='Path to the yaml config file')
   
def main():
    args = parser.parse_args()
    generate(args.config)