import os, sys

import time
import subprocess

import numpy as np
import pandas as pd

import argparse as arg
import concurrent.futures

# Load Config
import tomli
import logging

from pcaputils import *

def main():
    pcap_path = mkpath_abs(PCAP_PATH)
    export_path = mkpath_abs(EXPORT_PATH)

    if not os.path.exists(pcap_path):
        logging.error("PCAP path not found")
        sys.exit(1)
    if not os.path.exists(export_path):
        logging.error("Export path not found")
        sys.exit(1)

    tasks = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONC_THREAD) as executor:
        for pcap_filepath in ls_subfolders(PCAP_PATH):
            export_filepath = os.path.splitext(os.path.join(export_path, pcap_filepath[len(pcap_path)+1:]))[0]
            export_filename = os.path.basename(export_filepath)
            export_parentdir = os.path.dirname(export_filepath)
            export_summary_parentdir = os.path.join(export_parentdir, 'summary')
            export_summarypath = os.path.join(export_summary_parentdir, export_filename)

            # create dir for export file
            mkdir_by_path(export_parentdir)
            mkdir_by_path(export_summary_parentdir)

            tasks.append(executor.submit(worker_summary, pcap_filepath, f'{export_summarypath}'))
            logging.info(f"Sumarizing {pcap_filepath} to {export_summarypath}")

        for task in concurrent.futures.as_completed(tasks):
            result = task.result()
            logging.info(f'Finished sumarizing: {result[1]}')


if __name__ == "__main__":
    try:
        try:
            with open("config.toml", "rb") as f:
                toml_dict = tomli.load(f)
        except FileNotFoundError:
            logging.critical("Invalid TOML file.")
            sys.exit(1)
        except tomli.TOMLDecodeError:
            logging.critical("Decoding error TOML file.")
            sys.exit(1)

        parser = arg.ArgumentParser()
        parser.add_argument("-o", "--overide", default=0, type=int)
        args = parser.parse_args()

        CONC_THREAD = toml_dict["CONC_THREAD"]

        OVERIDE = args.overide
        PCAP_PATH = toml_dict["PCAP_PATH"]
        EXPORT_PATH = toml_dict["SAVED_PATH"]

        # Create logger
        file_handler = logging.FileHandler(filename="test.log", mode="w")
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        handlers = [file_handler, stdout_handler]

        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
            handlers=handlers,
        )
        main()

    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except Exception as e:
        raise e
