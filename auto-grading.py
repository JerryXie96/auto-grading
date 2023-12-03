# -*- coding: utf-8 -*-

from typing import Dict, Tuple
from schema import Schema, SchemaError

from scheme import scheme

import argparse
import os
import sys

import pandas as pd
import yaml

def err_exit(message: str) -> None:
    print(message, file=sys.stderr)
    exit(1)

def rename(directory: str, filename: str, new_name: str) -> None:
    file_path = os.path.join(directory, filename)
    if os.path.exists(file_path):
        new_path = os.path.join(directory, new_name)
        os.rename(file_path, new_path)
    return
    
def read_csv(config: Dict, used_field: str) -> pd.DataFrame:
    try:
        ret = pd.read_csv(config[used_field]['file'], delimiter=config[used_field]['delimiter'], keep_default_na=False)
    except:
        err_exit('Cannot load files about ' + used_field)
    return ret

def stu_ans_preprocessing(config: Dict) -> Dict:
    stu_ans = {}
    failed = pd.DataFrame()
    failed['filename'] = ''
    stu_ans_csv = read_csv(config, 'stu_answers')
    
    for idx, row in stu_ans_csv.iterrows():
        is_failed = False
        stu_id_keys = []    # keys about student IDs in this row
        ans_id_keys = []    # keys about answers in this row
        
        # put them in order
        for key in row.keys():
            if key.startswith(config['stu_answers']['answer_prefix']):
                ans_id_keys.append(key)
            elif key.startswith(config['stu_answers']['id_prefix']):
                stu_id_keys.append(key)
        stu_id_keys.sort()
        ans_id_keys.sort()
        
        # get student ID
        stu_id = ''
        for digit_key in stu_id_keys:
            try:
                stu_id += str(int(row[digit_key]))
            except:
                # cannot recognize the student ID
                failed.loc[len(failed.index)] = [row['File name']]
                is_failed = True
                break
        
        # if failed, go to the next student
        if is_failed:
            continue
        
        if config['scan_img']['need_rename']:
            rename(config['scan_img']['path'], row['File name'] + config['scan_img']['extension'], stu_id + config['scan_img']['extension'])
        
        stu_ans[stu_id] = {}
        for ans_key in ans_id_keys:
            stu_ans[stu_id][ans_key.split('.')[1]] = row[ans_key].split('|')
    
    # write the list of failed students to a file
    failed.to_csv(config['failed_stu']['file'])
    
    return stu_ans

def correct_ans_preprocessing(config: Dict) -> Dict:
    correct_ans = {}
    correct_ans_csv = pd.read_csv(config['correct_ans']['file'], delimiter=config['correct_ans']['delimiter'])
    
    for idx, row in correct_ans_csv.iterrows():
        try:
            correct_ans[row['question']] = {}
            correct_ans[row['question']]['ans'] = row['correct_answer'].split('|')
            correct_ans[row['question']]['marks'] = float(row['marks'])
            if row['isMultiple'] == 'T':
                correct_ans[row['question']]['isMultiple'] = True
            else:
                correct_ans[row['question']]['isMultiple'] = False
        except:
            err_exit('Cannot load the data of correct answers.')
    
    return correct_ans

def grading(stu_ans: Dict, correct_ans: Dict) -> Tuple[Dict, Dict]:
    stu_ans_table = {}
    stu_marks = {}
    for student in stu_ans.keys():
        marks = 0
        stu_ans_table[student] = {}
        for question in correct_ans.keys():
            if set(correct_ans[question]['ans']) == set(stu_ans[student][question]):
                marks += correct_ans[question]['marks']
                stu_ans_table[student][question] = 'C'
            else:
                stu_ans_table[student][question] = 'Wrong'
        stu_marks[student] = {'marks': marks}
    return stu_ans_table, stu_marks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto-grading tool with FormScanner')
    parser.add_argument('-c', '--config', help='Path of config file', required=True)
    args = parser.parse_args()
    
    print('Loading config file.')
    try:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
    except:
        err_exit('Cannot load the config file.')
    
    schema = Schema(scheme)
    try:
        schema.validate(config)
    except SchemaError as se:
        print(se)
        exit(1)

    print('Preprocessing answers of students.')
    stu_ans = stu_ans_preprocessing(config)
    
    print('Preprocessing correct answers.')
    correct_ans = correct_ans_preprocessing(config)
    
    print('Grading students.')
    stu_ans_table, stu_marks = grading(stu_ans, correct_ans)
    
    print('Generating output files.')
    stu_ans_table_df = pd.DataFrame.from_dict(stu_ans_table)
    stu_marks_df = pd.DataFrame.from_dict(stu_marks)
    stu_ans_table_df.to_csv(config['outputs']['ans_table'])
    stu_marks_df.to_csv(config['outputs']['marks'])
    