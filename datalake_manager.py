"""
Julyan van der Westhuizen
17/07/25

This file describes management infrastructure to abstract file handling away. 
In real-world scenarios, we'd use enterprise solutions in place filesystems for blob storage etc. 
This addition is meant to simulate / abstract away that component.
When incorporating proper enterprise solutions, this class can be altered - leaving other components untouched. 
"""

import os
import json
import shutil
from datetime import datetime
from pipeline_log_manager import shared_logger

class LakeManager:

    def __init__(self):
         # Get the absolute path to the folder where this file lives (your project root)
        project_root = os.path.dirname(os.path.abspath(__file__))

        self.tims_raw_dir_location = f"{project_root}/datalake/raw/tims"
        self.tims_transformed_dir_location = f"{project_root}/datalake/transformed/tims"
        self.processed_dir = f"{project_root}/datalake/processed"

        # some settings
        self.retain_window_size = 2

        # File Structure Auto-Setup
        os.makedirs(self.tims_raw_dir_location, exist_ok=True)
        os.makedirs(self.tims_transformed_dir_location, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    # DATASTREAM-SPECIFIC METHODS

    def write_TIMS_raw_snapshot(self, raw_data):
        # Create filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = self.tims_raw_dir_location + "/"+  f"TIMS-raw-snapshot-{timestamp}.json"

        # Write to file
        with open(filename, "w") as f:
            json.dump(raw_data, f)

        shared_logger.log(f"Wrote RAW snapshot: {filename}")

    def read_TIMS_raw_snapshot(self):
        # Read in every file in the dir, read in every data item
        data = []

        # Batch read files
        for filename in os.listdir(self.tims_raw_dir_location):
            filepath = self.tims_raw_dir_location + "/" + filename

            with open(filepath, "r") as f:
                data.append(json.load(f))

            shared_logger.log(f"Read RAW snapshot: {filename}")
            self.move_snapshot_to_processed(filepath, filename)

        #return a 2D array
        return data
    
    def write_TIMS_transformed_snapshot(self, transformed_data):
        # Create the filename
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = self.tims_transformed_dir_location + "/" + f"TIMS-transformed-snapshot-{timestamp}.json"

        # Write to file
        with open(filename, "w") as f:
            dumped_data = []

            for d in transformed_data:
                dumped_data.append(d.model_dump()) # converts pydantic objects to python dicts

            json.dump(dumped_data, f, indent=2, default=str)

        shared_logger.log(f"Wrote TRANSFORMED snapshot: {filename}")

    def read_TIMS_transformed_snapshot(self):
        # Read in every file in the dir, read in every data item per file
        data = []

        # Batch read files in the dir
        for filename in os.listdir(self.tims_transformed_dir_location):
            filepath = self.tims_transformed_dir_location + "/" + filename

            with open(filepath, "r") as f:
                data.append(json.load(f))

                shared_logger.log(f"READ TRANSFORMED snapshot: {filename}")
                self.move_snapshot_to_processed(filepath, filename)

        # return 2D array
        return data

    def move_snapshot_to_processed(self, filepath, filename):
        # mark the snapshot
        new_filename = "PROCESSED-" + filename
        processed_path = self.processed_dir + "/" + new_filename
        shutil.move(filepath, processed_path)

    def retain_snapshot_window(self):
        # Goes through the processed snapshots, retains the n latest ones, deletes the rest 
        # Keeps a window of snapshots

        snapsots_names = os.listdir(self.processed_dir)
        raw_snapshots_names = []
        transformed_snapshots_names = []

        for s in snapsots_names:
            if "raw" in s:
                raw_snapshots_names.append(s)
            if "transformed" in s:
                transformed_snapshots_names.append(s)


        raw_snapshots_names.sort()
        transformed_snapshots_names.sort()

        num_raw = len(raw_snapshots_names)
        if num_raw > self.retain_window_size:
            for s in raw_snapshots_names[:num_raw - self.retain_window_size]:
                os.remove(os.path.join(self.processed_dir, s))
                shared_logger.log(f"Deleted old RAW snapshot: {s}")

        num_trans = len(transformed_snapshots_names)
        if num_trans > self.retain_window_size:
            for s in transformed_snapshots_names[:num_trans - self.retain_window_size]:
                os.remove(os.path.join(self.processed_dir, s))
                shared_logger.log(f"Deleted old TRANSFORMED snapshot: {s}")

