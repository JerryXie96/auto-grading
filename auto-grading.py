# -*- coding: utf-8 -*-

from typing import Dict

import argparse
import sys

import pandas as pd
import yaml

def err_exit(message: str) -> None:
    print(message, file=sys.stderr)
    exit(1)
    
def read_csv(config: Dict, used_field: str) -> pd.DataFrame:
    try:
        ret = pd.read_csv(config[used_field]['file'], delimiter=config[used_field]['delimiter'])
    except:
        err_exit('Cannot load files about ' + used_field)
    return ret

def student_ans_preprocessing(config: Dict) -> Dict:
    students_ans = {}
    students_ans_csv = read_csv(config, 'std_answers')
    
    for idx, row in students_ans_csv.iterrows():
        student_id_keys = []
        answers_id_keys = []
        for key in row.keys():
            if key.startswith(config['std_answers']['answer_prefix']):
                answers_id_keys.append(key.split('.')[1])
            elif key.startswith(config['std_answers']['id_prefix']):
                student_id_keys.append(key.split('.')[1])
        student_id_keys.sort()
        answers_id_keys.sort()
    
    return students_ans

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto-grading tool with FormScanner')
    parser.add_argument('-c', '--config', help='Path of config file', required=True)
    args = parser.parse_args()
    
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except:
        err_exit('Cannot load the config file.')

    student_ans = student_ans_preprocessing(config)
    