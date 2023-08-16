import os
import glob
import csv
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
import re
import pandas as pd

# Read all files from a folder location including subfolders
# Identify individual measurement jobs
# Write results in a csv table format (row of values per measurement)
def parse_logs_to_csv(folder_path, output_file_location):
    csv_files = glob.glob(os.path.join(folder_path, '**', '*.csv'), recursive=True)
    measure_results_row = [] # list of measurement jobs
    measure_results_data = {
        'Timestamp' : None,
        'Measurement_ID' : ""
    }
    reading_job = False # parsing stage = reading in measurement values

    for csv_file in csv_files:
        with open(csv_file, 'r') as file:
            input_text = file.read()
            pattern = re.compile(r"""
                                 (?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3};\ ;\ ;S;\ -\ )ASCCS\ Start\ Measurement\ Message\ received(\r\n|\r|\n)
                                 (?P=timestamp)(?P=fill)Measurement\ ID:\s*(?P<measurement_id>\w*-\w*-\w*-\w*-\w*)(\r\n|\r|\n)
                                 (?P=timestamp)(?P=fill)Lane:\s*(?P<lane>\d)(\r\n|\r|\n)
                                 (?P=timestamp)(?P=fill)Task:\s*(?P<task_num>\d)\s*-\s*(?P<task_str>\w*)\s*(\r\n|\r|\n)
                                 (?P=timestamp)(?P=fill)Pos:\s*(?P<pos_num>\d)\s*-\s*(?P<pos_str>\w*)
                                 """, re.VERBOSE)

            matches = pattern.finditer(input_text)
            if matches:
                for match in matches:
                    print(match.groupdict()['pos_str'])
            else:
                print("No matches found.")

            # print(f"Contents of {csv_file}:")
            # print(file.read())
            #print("=" * 40)
            #   

def collect_jobs(folder_path, output_file_location):
    csv_files = glob.glob(os.path.join(folder_path, '**', 'MeasureResult*.csv'), recursive=True)
    
    measure_results = [] # list of measurement jobs


    for csv_file in csv_files:
        measure_results_data = init_measure_results_data()
        with open(csv_file, 'r') as file:
            log_lines = file.read()

            # for log_line in log_lines:
            #     pass # Kesken!!!!
        # Search START OF JOB
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )ASCCS Start Measurement Message received')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Timestamp'] = parse_timestamp(match.groupdict()['timestamp'])

        # Search MEASUREMENT ID
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Measurement ID:\s*(?P<measurement_id>\w*-\w*-\w*-\w*-\w*)')
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
            measure_results_data['Task_str'] = match.groupdict()['task_str']

        # Search POS
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Pos:\s*(?P<pos_num>\s*\d*)\s*-\s*(?P<pos_str>\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Pos_num'] = match.groupdict()['pos_num']
            measure_results_data['Pos_str'] = match.groupdict()['pos_str']

        # Search LEN
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Len:\s*(?P<len_num>\s*\d*)\s*-\s*(?P<len_str>\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Len_num'] = match.groupdict()['len_num']
            measure_results_data['Len_str'] = match.groupdict()['len_str']

        # Search TYPE
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Type:\s*(?P<type_num>\s*\d*)\s*-\s*(?P<type_str>\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Type_num'] = match.groupdict()['type_num']
            measure_results_data['Type_str'] = match.groupdict()['type_str']

        # Search CONTAINER LENGTH
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Length:\s*(?P<c_length>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Cont_Length'] = match.groupdict()['c_length']

        # Search CONTAINER WIDTH
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Width:\s*(?P<c_width>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Cont_Width'] = match.groupdict()['c_width']

        # Search CONTAINER HEIGHT
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Height:\s*(?P<c_height>\s*\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Cont_Height'] = match.groupdict()['c_height']
        
        # Search ASSUMING TRAILER
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Assuming\s*(?P<assuming_trailer>\w*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Assuming_trailer'] = match.groupdict()['assuming_trailer']

        # Search POINT CENTER
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Point Center X\/Y\/Z:\s*(?P<p_center_x>\d*)\s*\/\s*(?P<p_center_y>\d*)\s*\/\s*(?P<p_center_z>\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Point_Center_X'] = match.groupdict()['p_center_x']
            measure_results_data['Point_Center_Y'] = match.groupdict()['p_center_y']
            measure_results_data['Point_Center_Z'] = match.groupdict()['p_center_z']

        # Search SKEW
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Skew:\s*(?P<skew>-?\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Skew'] = match.groupdict()['skew']

        # Search TILT
        pattern = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Tilt\s*(?P<tilt>-?\d*)')
        match = pattern.search(log_lines)
        if match:
            measure_results_data['Tilt'] = match.groupdict()['tilt']

        measure_results.append(measure_results_data)

    return measure_results

def init_measure_results_data():
    measure_results_data = {
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
        'Assuming_trailer' : None,
        'Point_Center_X' : None,
        'Point_Center_Y' : None,
        'Point_Center_Z' : None,
        'Skew' : None,
        'Tilt' : None,
        'N_of_TWL_detected' : None, 
        'N_of_TWL_calculated' : None
    }
    
    return measure_results_data

def parse_timestamp(match_timestamp):
    return datetime.strptime(match_timestamp, r'%d.%m.%Y %H:%M:%S;%f')

def main():
    root = tk.Tk()
    root.withdraw()

    log_folder_path = filedialog.askdirectory()
    output_file_location = "output/results"
    # parse_logs_to_csv(log_folder_path, output_file_location)
    df = pd.DataFrame.from_dict(collect_jobs(log_folder_path, output_file_location))
    df.to_csv('Measureresults.csv')

if __name__ == "__main__":
    main()