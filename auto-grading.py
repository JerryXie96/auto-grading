# -*- coding: utf-8 -*-

from typing import List

import argparse
import sys

import pandas as pd
import yaml

def err_exit(message: str) -> None:
    print(message, file=sys.stderr)
    exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto-grading tool with FormScanner')
    parser.add_argument('-c', '--config', help='Path of config file', required=True)
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except:
        err_exit('Cannot load the config file.')

    try:
        students_ans = pd.read_csv(config['std_answers']['file'], delimiter=config['std_answers']['delimiter'])
    except:
        err_exit('Cannot load student answers.')
    
    
    