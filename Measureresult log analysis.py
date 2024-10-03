import os
import time
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

    # Get all csv files in the folder and subfolders
    csv_files = glob.glob(os.path.join(folder_path, '**', 'MeasureResult*.[cC][sS][vV]'), recursive=True)

    # Initialize list of measurement jobs
    measure_results = [] # list of measurement jobs

    for csv_file in csv_files:

        # Initialize dictionary to store measurement job data
        measure_results_data = init_measure_results_data()

        # open csv file
        with open(csv_file, 'r') as file:

            # Extract csv filename
            measure_results_data['filename'] = os.path.basename(csv_file)

            # Initialize patterns
            pattern_START_OF_JOB = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )ASCCS Start Measurement Message received')
            pattern_MEASUREMENT_ID = re.compile(r'Measurement ID:\s*(?P<measurement_id>Man|\w*-\w*-\w*-\w*-\w*|measurement_id_\d+)')
            pattern_LANE = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Lane:\s*(?P<lane>\s*\d*)')
            pattern_TASK = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Task:\s*(?P<task_num>\s*\d*)\s*-\s*(?P<task_str>\w*)')
            pattern_POS = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Pos:\s*(?P<pos_num>\s*\d*)\s*-\s*(?P<pos_str>\w*)')
            pattern_LEN = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Len:\s*(?P<len_num>Not Available|\d+)\s*-\s(?P<len_str>Not Available|\w*)')
            pattern_TYPE = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Type:\s*(?P<type_num>\s*\d*)\s*-\s*(?P<type_str>.*)')
            pattern_CONT_LENGTH = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Length:\s*(?P<c_length>\s*\d*)')
            pattern_CONT_WIDTH = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Width:\s*(?P<c_width>\s*\d*)')
            pattern_CONT_HEIGHT = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Cont. Height:\s*(?P<c_height>\s*\d*)')
            pattern_LANE_STATUS = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )LaneStat\s*-\s*(?P<lane_status>\w*)')
            pattern_MEASUREMENT_STATUS = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )\s\|\s*MeasStat\s*-\s*(?P<meas_status>\w*)')
            pattern_ASSUMING_TRAILER = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Assuming\s*(?P<assuming_trailer>\w*)')
            pattern_POINT_CENTER = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Point Center X\/Y\/Z:\s*(?P<p_center_x>\d*)\s*\/\s*(?P<p_center_y>\d*)\s*\/\s*(?P<p_center_z>\d*)')
            pattern_SKEW = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Skew:\s*(?P<skew>-?\d*)')
            pattern_TILT = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; - )Tilt\s*(?P<tilt>-?\d*)')
            pattern_TWL_DETECTED = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; -- )Number of detected twist locks \(TL\):\s*(?P<det_twl>-?\d*)')
            pattern_TWL_CALCULATED = re.compile(r'(?P<timestamp>\d{2}\.\d{2}\.\d{4}\ \d{2}:\d{2}:\d{2};\d{3})(?P<fill>;\d{3}; ; ;S; -- )Number of calculated twist locks \(TL\):\s*(?P<calc_twl>-?\d*)')

            # Record the start time
            start_time = time.time()

            # Read csv file line by line
            for line_index, log_line in enumerate(file, start=1):

                # Search START OF JOB
                match = pattern_START_OF_JOB.search(log_line)
                if match:
                    measure_results_data['Timestamp'] = parse_timestamp(match.groupdict()['timestamp'])
                    measure_results_data['Date'] = parse_date(match.groupdict()['timestamp'])
                    continue

                # Search MEASUREMENT ID
                match = pattern_MEASUREMENT_ID.search(log_line)
                if match:
                    measure_results_data['Measurement_ID'] = match.groupdict()['measurement_id']
                    continue

                # Search LANE
                match = pattern_LANE.search(log_line)
                if match:
                    measure_results_data['Lane'] = match.groupdict()['lane']
                    continue

                # Search TASK
                match = pattern_TASK.search(log_line)
                if match:
                    measure_results_data['Task_num'] = match.groupdict()['task_num']
                    measure_results_data['Task_str'] = match.groupdict()['task_str'].rstrip()
                    continue

                # Search POS
                match = pattern_POS.search(log_line)
                if match:
                    measure_results_data['Pos_num'] = match.groupdict()['pos_num']
                    measure_results_data['Pos_str'] = match.groupdict()['pos_str'].rstrip()
                    continue

                # Search LEN
                match = pattern_LEN.search(log_line)
                if match:
                    measure_results_data['Len_num'] = match.groupdict()['len_num']
                    measure_results_data['Len_str'] = match.groupdict()['len_str'].rstrip()
                    continue

                # Search TYPE
                match = pattern_TYPE.search(log_line)
                if match:
                    measure_results_data['Type_num'] = match.groupdict()['type_num']
                    measure_results_data['Type_str'] = match.groupdict()['type_str'].rstrip()
                    continue

                # Search CONTAINER LENGTH
                match = pattern_CONT_LENGTH.search(log_line)
                if match:
                    measure_results_data['Cont_Length'] = int(match.groupdict()['c_length'])
                    continue

                # Search CONTAINER WIDTH
                match = pattern_CONT_WIDTH.search(log_line)
                if match:
                    measure_results_data['Cont_Width'] = int(match.groupdict()['c_width'])
                    continue

                # Search CONTAINER HEIGHT
                match = pattern_CONT_HEIGHT.search(log_line)
                if match:
                    measure_results_data['Cont_Height'] = int(match.groupdict()['c_height'])
                    continue
                
                # Search LANE STATUS
                match = pattern_LANE_STATUS.search(log_line)

                if match:
                    if measure_results_data['Init_lane_status'] == None:
                        measure_results_data['Init_lane_status'] = match.groupdict()['lane_status'].rstrip()
                    else:
                        measure_results_data['Last_lane_status'] = match.groupdict()['lane_status'].rstrip()
                    continue
                
                # Search MEASUREMENT STATUS
                match = pattern_MEASUREMENT_STATUS.search(log_line)
     
                if match:
                    if measure_results_data['Init_meas_status'] == None:
                        measure_results_data['Init_meas_status'] = match.groupdict()['meas_status'].rstrip()
                    else:
                        measure_results_data['Last_meas_status'] = match.groupdict()['meas_status'].rstrip()
                    continue

                # Search ASSUMING TRAILER
                match = pattern_ASSUMING_TRAILER.search(log_line)

                if match:
                    measure_results_data['Assuming_trailer'] = match.groupdict()['assuming_trailer'].rstrip()
                    continue

                # Search POINT CENTER
                match = pattern_POINT_CENTER.search(log_line)

                if match:
                    measure_results_data['Point_Center_X'] = int(match.groupdict()['p_center_x'])
                    measure_results_data['Point_Center_Y'] = int(match.groupdict()['p_center_y'])
                    measure_results_data['Point_Center_Z'] = int(match.groupdict()['p_center_z'])
                    continue

                # Search SKEW
                match = pattern_SKEW.search(log_line)

                if match:
                    measure_results_data['Skew'] = int(match.groupdict()['skew'])
                    continue

                # Search TILT
                match = pattern_TILT.search(log_line)

                if match:
                    measure_results_data['Tilt'] = int(match.groupdict()['tilt'])
                    continue

                # Search TWL or container edges detected
                match = pattern_TWL_DETECTED.search(log_line)

                if match:
                    measure_results_data['N_of_TWL_detected'] = int(match.groupdict()['det_twl'])
                    continue

                # Search TWL or container edges calculated
                match = pattern_TWL_CALCULATED.search(log_line)

                if match:
                    measure_results_data['N_of_TWL_calculated'] = int(match.groupdict()['calc_twl'])
                    continue

        # Define TLMS success
        if measure_results_data['Task_str'] != None:
            if measure_results_data['Init_meas_status'] == 'InProgr':
                if measure_results_data['Last_meas_status'] == 'Done':
                    measure_results_data['TLMS_success'] = 1
                elif measure_results_data['Last_meas_status'] == 'Failed':
                    measure_results_data['TLMS_success'] = 0

        # Record the end time
        end_time = time.time()

        # Calculate elapsed time
        elapsed_time = end_time - start_time
        print(f"Elapsed time for processing {measure_results_data['filename']}: {line_index} lines, {elapsed_time:.3f} seconds")


        measure_results.append(measure_results_data)

    return measure_results

def init_measure_results_data():
    measure_results_data = {
        'filename' : None,
        'Timestamp' : None,
        'Date' : None,
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

def parse_date(match_timestamp):
    return match_timestamp.split()[0].replace(".", "")

def main():
    root = tk.Tk()
    root.withdraw()

    log_folder_path = filedialog.askdirectory()
    output_file_location = "output/results"
    # parse_logs_to_csv(log_folder_path, output_file_location)
    df = pd.DataFrame.from_dict(collect_jobs(log_folder_path, output_file_location))
    df.to_csv('Measureresults.csv')
    df.to_excel('Measureresult.xlsx')
    print("Done!")

if __name__ == "__main__":
    main()