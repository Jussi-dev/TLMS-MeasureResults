import os
import glob
import csv
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import re
import pandas as pd
from enum import Enum

class State(Enum):
    INIT            = 0
    SEARCH_JOB_INFO = 1
    SEARCH_STATUSES = 2

# Read all files from a folder location including subfolders
# Identify individual measurement jobs
# Write results in a csv table format (row of values per measurement)
def parse_logs_to_csv(folder_path, output_file_location):
    csv_files = glob.glob(os.path.join(folder_path, '**', 'MeasureResult*.csv'), recursive=True)
    
    parsing_state = State.INIT
    
    for csv_file in csv_files:
        measure_results_data = init_measure_results_data()
        with open(csv_file, 'r') as file:
            log_lines = file.readlines()

        for log_line in log_lines:

            if parsing_state is State.INIT:
                measure_results = [] # list of measurement jobs
                parsing_state = State.SEARCH_JOB_INFO

            elif parsing_state is State.SEARCH_JOB_INFO:
                pass

def collect_jobs(folder_path, output_file_location):
    csv_files = glob.glob(os.path.join(folder_path, '**', 'MeasureResult*.[cC][sS][vV]'), recursive=True)
    measure_results = [] # list of measurement jobs

    for csv_file in csv_files:
        measure_results_data = init_measure_results_data()
        with open(csv_file, 'r') as file:
            log_lines = file.read()

        #Filename
        measure_results_data['filename'] = os.path.basename(csv_file)

        # Search START OF JOB
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )ASCCS Start Measurement Message received')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Timestamp'] = parse_timestamp(match.groupdict()['timestamp'])

        # Search MEASUREMENT ID
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Measurement ID:\s*(?P<measurement_id>Man|\w*-\w*-\w*-\w*-\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Measurement_ID'] = match.groupdict()['measurement_id']

        # Search LANE
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Lane:\s*(?P<lane>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Lane'] = match.groupdict()['lane']

        # Search TASK
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Task:\s*(?P<task_num>\s*\d*)\s*-\s*(?P<task_str>\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Task_num'] = match.groupdict()['task_num']
            measure_results_data['Task_str'] = match.groupdict()['task_str'].rstrip()

        # Search POS
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Pos:\s*(?P<pos_num>\s*\d*)\s*-\s*(?P<pos_str>\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Pos_num'] = match.groupdict()['pos_num']
            measure_results_data['Pos_str'] = match.groupdict()['pos_str'].rstrip()

        # Search LEN
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Len:\s*(?P<len_num>Not Available|\d+)\s*-\s(?P<len_str>Not Available|\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Len_num'] = match.groupdict()['len_num']
            measure_results_data['Len_str'] = match.groupdict()['len_str'].rstrip()

        # Search TYPE
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Type:\s*(?P<type_num>\s*\d*)\s*-\s*(?P<type_str>.*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Type_num'] = match.groupdict()['type_num']
            measure_results_data['Type_str'] = match.groupdict()['type_str'].rstrip()

        # Search CONTAINER LENGTH
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Length:\s*(?P<c_length>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Cont_Length'] = int(match.groupdict()['c_length'])

        # Search CONTAINER WIDTH
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Width:\s*(?P<c_width>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Cont_Width'] = int(match.groupdict()['c_width'])

        # Search CONTAINER HEIGHT
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Height:\s*(?P<c_height>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Cont_Height'] = int(match.groupdict()['c_height'])
        
        # Search LANE STATUS
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )LaneStat\s*-\s*(?P<lane_status>\w*)')
        matches = pattern.finditer(log_lines)

        first_match = next(matches, None)

        last_match = None

        for match in matches:
            last_match = match
        if first_match:
            measure_results_data['Init_lane_status'] = first_match.groupdict()['lane_status'].rstrip()
        if last_match:
            measure_results_data['Last_lane_status'] = last_match.groupdict()['lane_status'].rstrip()

        # Search MEASUREMENT STATUS
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )\s*\| MeasStat\s*-\s*(?P<meas_status>\w*)')
        matches = pattern.finditer(log_lines)

        first_match = next(matches, None)

        last_match = None

        for match in matches:
            last_match = match
        if first_match:
            measure_results_data['Init_meas_status'] = first_match.groupdict()['meas_status'].rstrip()
        if last_match:
            measure_results_data['Last_meas_status'] = last_match.groupdict()['meas_status'].rstrip()

        # Search ASSUMING TRAILER
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Assuming\s*(?P<assuming_trailer>\w*)')
        matches = pattern.finditer(log_lines)

        last_match = None

        for match in matches:
            last_match = match
        if last_match:
            measure_results_data['Assuming_trailer'] = match.groupdict()['assuming_trailer'].rstrip()

        # Search POINT CENTER
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Point Center X\/Y\/Z:\s*(?P<p_center_x>\d*)\s*\/\s*(?P<p_center_y>\d*)\s*\/\s*(?P<p_center_z>\d*)')
        matches = pattern.finditer(log_lines)

        last_match = None

        for match in matches:
            last_match = match
        if last_match:
            measure_results_data['Point_Center_X'] = int(match.groupdict()['p_center_x'])
            measure_results_data['Point_Center_Y'] = int(match.groupdict()['p_center_y'])
            measure_results_data['Point_Center_Z'] = int(match.groupdict()['p_center_z'])

        # Search SKEW
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Skew:\s*(?P<skew>-?\d*)')
        matches = pattern.finditer(log_lines)

        last_match = None

        for match in matches:
            last_match = match
        if last_match:
            measure_results_data['Skew'] = int(match.groupdict()['skew'])

        # Search TILT
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Tilt\s*(?P<tilt>-?\d*)')
        matches = pattern.finditer(log_lines)

        last_match = None

        for match in matches:
            last_match = match
        if last_match:
            measure_results_data['Tilt'] = int(match.groupdict()['tilt'])

        # Search TWL or container edges detected
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; -- )(?:Number of detected twist locks \(TL\):|Number of detected container edges \(CE\):)\s*(?P<det_twl>-?\d*)')
        matches = pattern.finditer(log_lines)

        last_match = None

        for match in matches:
            last_match = match
        if last_match:
            measure_results_data['N_of_TWL_detected'] = int(match.groupdict()['det_twl'])

        # Search TWL or container edges calculated
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; -- )(?:Number of calculated twist locks \(TL\):|Number of calculated container edges \(CE\):)\s*(?P<calc_twl>-?\d*)')
        matches = pattern.finditer(log_lines)

        last_match = None

        for match in matches:
            last_match = match
        if last_match:
            measure_results_data['N_of_TWL_calculated'] = int(match.groupdict()['calc_twl'])

        # Define TLMS success
        if measure_results_data['Task_str'] != None:
            if measure_results_data['Init_meas_status'] == 'InProgr':
                if measure_results_data['Last_meas_status'] == 'Done':
                    measure_results_data['TLMS_success'] = 1
                elif measure_results_data['Last_meas_status'] == 'Failed':
                    measure_results_data['TLMS_success'] = 0

        measure_results.append(measure_results_data)

    return measure_results

def init_measure_results_data():
    measure_results_data = {
        'filename' : None,
        'Timestamp' : None,
        'Measurement_ID' : None,
        'Lane' : None,
        'Task_num' : None,
        'Task_str' : None,
        'Pos_num' : None,
        'Pos_str' : None,
        'Len_num' : None,
        'Len_str' : None,
        'Type_num' : None,
        'Type_str' : None,
        'Cont_Length' : None,
        'Cont_Width' : None,
        'Cont_Height' : None,
        'Init_lane_status' : None,
        'Init_meas_status' : None,
        'Last_lane_status' : None,
        'Last_meas_status' : None,
        'Assuming_trailer' : None,
        'Point_Center_X' : None,
        'Point_Center_Y' : None,
        'Point_Center_Z' : None,
        'Skew' : None,
        'Tilt' : None,
        'N_of_TWL_detected' : None, 
        'N_of_TWL_calculated' : None,
        'TLMS_success' : None

    }
    
    return measure_results_data

def parse_timestamp(match_timestamp):
    return datetime.strptime(match_timestamp, '%d.%m.%Y %H:%M:%S;%f')

def main():
    root = tk.Tk()
    root.withdraw()

    log_folder_path = filedialog.askdirectory()
    output_file_location = "output/results"
    # parse_logs_to_csv(log_folder_path, output_file_location)
    df = pd.DataFrame.from_dict(collect_jobs(log_folder_path, output_file_location))
    df.to_csv('Measureresults.csv')
    df.to_excel('Measureresult.xlsx')

if __name__ == "__main__":
    main()