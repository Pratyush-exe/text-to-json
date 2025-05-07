import logging
import time
import json
import os

from t2j.prem_sdk import PremSDK  
from t2j.prompts import Prompts
from t2j.chunker import DocumentChunker
from t2j.decomposer import SchemaDecomposer
from t2j.extractor import FieldExtractor
from t2j.utils import *


class Workflow:
    def __init__(self, trace_id: str, log_dir="logs"):
        self.trace_id = trace_id
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, f"{trace_id}.log")
        self.logger = self._setup_logger(trace_id)

    def _setup_logger(self, trace_id):
        logger = logging.getLogger(f"Text2JsonLogger_{trace_id}")
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        if logger.hasHandlers():
            logger.handlers.clear()

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def get_latest_logs(self, last_position=0):
        """Read new log entries since last_position"""
        try:
            with open(self.log_file, 'r') as f:
                f.seek(last_position)
                new_logs = f.read()
                new_position = f.tell()
                return new_logs, new_position
        except FileNotFoundError:
            return "", last_position

    def run(self, file_path, schema_path):
        try:
            print("STARTING WORKFLOW")
            total_start_time = time.time()

            # Setup
            setup_start = time.time()
            chunk_size_lines = 100
            promptsClass = Prompts()
            model = PremSDK()
            chunker = DocumentChunker(prompts=promptsClass, model=model)
            setup_end = time.time()
            print(f"SETUP COMPLETED in {setup_end - setup_start:.2f} seconds")

            # Step 1: Chunking
            step1_start = time.time()
            chunks = chunker.smart_chunk(file_path, chunk_size_lines)
            other_data = chunker.extract_other_info(file_path)
            for d in other_data:
                chunks[d['heading']] = {
                    'content': d['content'] if type(d['content']) == str else "\n".join(d['content']),
                    "sub-headings": []
                }
            step1_end = time.time()
            print(f"STEP 1 COMPLETED in {step1_end - step1_start:.2f} seconds")
            self.logger.debug(f"Chunks: {json.dumps(chunks, indent=2)}")

            # Step 2: Decomposition
            step2_start = time.time()
            with open(schema_path, 'r') as f:
                schema_dict = json.load(f)
            decomposer = SchemaDecomposer(schema_dict, traversal_limit=1)
            schema_tree = decomposer.decompose()
            step2_end = time.time()
            print(f"STEP 2 COMPLETED in {step2_end - step2_start:.2f} seconds")
            self.logger.debug(f"Schema Decomposition Output: {json.dumps(schema_tree, indent=2)}")

            # Step 3: Print Schema Tree
            step3_start = time.time()
            decomposer.print_schema_tree(schema_tree, indent=4)
            step3_end = time.time()
            print(f"STEP 3 COMPLETED in {step3_end - step3_start:.2f} seconds")

            # Step 4: Extraction
            step4_start = time.time()
            extractor = FieldExtractor(model, promptsClass)
            extracted_data = extractor.extract(chunks, schema_tree)
            step4_end = time.time()
            print(f"STEP 4 COMPLETED in {step4_end - step4_start:.2f} seconds")
            self.logger.debug(f"Extracted Data: {json.dumps(extracted_data, indent=2)}")

            # Step 5: Merge
            step5_start = time.time()
            final_output = merge(extracted_data)
            step5_end = time.time()
            print(f"STEP 5 COMPLETED in {step5_end - step5_start:.2f} seconds")
            self.logger.debug(f"Final Output: {json.dumps(final_output, indent=2)}")

            total_end_time = time.time()
            print(f"WORKFLOW COMPLETED in {total_end_time - total_start_time:.2f} seconds")

            return final_output

        except Exception as e:
            self.logger.error("An error occurred during workflow execution", exc_info=True)
            raise
