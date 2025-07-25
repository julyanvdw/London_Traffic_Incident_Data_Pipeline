"""
Julyan van der Westhuizen
18/07/25

This script is responsbile for linking the other components in the ETL pipeline
"""

from pipeline_log_manager import shared_logger
from extract import fetch_TIMS
from transform import transformer
from load import loader
from datalake_manager import LakeManager

def run_pipeline():

    shared_logger.log_pipeline_phase("STARTING PIPELINE")

    # run the Exctration Step
    shared_logger.log_pipeline_phase("EXTRACT")
    fetch_TIMS.fetch_tims_data() 
    
    # run the Transform Step
    shared_logger.log_pipeline_phase("TRANSFORM")
    transformer.ingest()

    # run the Load Step
    shared_logger.log_pipeline_phase("LOAD")
    loader.load()

    # maintain the snapshot window
    manager = LakeManager()
    manager.retain_snapshot_window()
    
    shared_logger.log_pipeline_phase("CLOSING PIPELINE")
    shared_logger.save_last_run_info()


if __name__ == "__main__":
    run_pipeline()

