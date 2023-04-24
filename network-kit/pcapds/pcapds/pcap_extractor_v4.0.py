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
    temp_path = mkpath_abs(TEMP_PATH)

    if not os.path.exists(pcap_path):
        logging.error("PCAP path not found")
        sys.exit(1)
    if not os.path.exists(export_path):
        logging.error("Export path not found")
        sys.exit(1)
    # Create temp folder
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    for pcap_filepath in ls_subfolders_ext(pcap_path, '.pcap'):
        # create export path        
        export_filepath = os.path.splitext(os.path.join(export_path, pcap_filepath[len(pcap_path)+1:]))[0]
        export_filename = os.path.basename(export_filepath)
        export_parentdir = os.path.dirname(export_filepath)
        export_summary_parentdir = os.path.join(export_parentdir, 'summary')
        export_summarypath = os.path.join(export_summary_parentdir, export_filename)

        # create dir for export file
        mkdir_by_path(export_parentdir)
        mkdir_by_path(export_summary_parentdir)
        
        # check file existed
        if (
            os.path.exists(f"{export_filepath}.csv")
            or os.path.exists(f"{export_filepath}.csv")
            and OVERIDE is False
        ):
            continue

        # split chunk of stream id range
        tcp_stream_len, udp_stream_len = stream_id_len(pcap_filepath, f'{export_summarypath}.csv')
        filesize = os.stat(pcap_filepath).st_size / 10**6

        # split stream id range
        tcp_stream_split, udp_stream_split = [], []
        if tcp_stream_len > 0:
            tcp_stream_split = stream_id_spliter(tcp_stream_len, filesize)
        if udp_stream_len > 0:
            udp_stream_split = stream_id_spliter(udp_stream_len, filesize)
        stream_split = {
            'tcp': tcp_stream_split,
            'udp': udp_stream_split
        }

        # check protocol existed
        # protocols = ls_protocol(pcap_filepath)

        logging.info(f"Processing file: {pcap_filepath} - udp: {udp_stream_len}, tcp: {tcp_stream_len} => exporting to: {export_filepath}.csv")
        start_time = time.time()

        # !TODO: add loop for each exist protocol
        filters = [
            # (http or http2 or (tls.app_data and not tls.handshake)) and tcp.payload and (tcp.port==443 or tcp.port==80)
            ('tcp', """-Y "(tcp.stream>={start_stream_id} and tcp.stream<={end_stream_id}) and (http or http2 or (tls.app_data and not tls.handshake)) and tcp.payload and (tcp.port==443 or tcp.port==80)" \
                       -T fields -e frame.time_epoch -e frame.number \
                       -e tcp.stream -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e ip.proto \
                       -e "_ws.col.Protocol" -e "_ws.col.Length" -e "_ws.col.Info" -e tcp.payload \
                       -E header=n -E separator=, -E quote=d -E occurrence=f"""), 
            
            ('udp', """-Y "(udp.stream>={start_stream_id} and udp.stream<={end_stream_id}) and quic.remaining_payload" \
                       -T fields -e frame.time_epoch -e frame.number \
                       -e udp.stream -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e ip.proto \
                       -e "_ws.col.Protocol" -e "_ws.col.Length" -e "_ws.col.Info" -e quic.remaining_payload \
                       -E header=n -E separator=, -E quote=d -E occurrence=f"""),
            
            # ('udp', """ -d udp.port==443,gquic \
            # -Y "(udp.stream>={start_stream_id} and udp.stream<={end_stream_id}) and gquic.payload" \
            # -T fields -e frame.time_epoch -e frame.number \
            # -e udp.stream -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e ip.proto \
            # -e "_ws.col.Protocol" -e "_ws.col.Length" -e "_ws.col.Info" -e "gquic.payload"\
            # -E header=n -E separator=, -E quote=d -E occurrence=f"""),
        ]

        for protocol, cmd_filter in filters:
            # create file
            if len(stream_split[protocol]) > 0:
                temp_protocol_filename = f"{temp_path}/{protocol}_{export_filename}"
                open(f"{temp_protocol_filename}.csv", "a").close()
                tasks = []
                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=CONC_THREAD) as pool:
                    for start_stream_id, end_stream_id in stream_split[protocol]:
                        tasks.append(
                            # !TODO: FIx this line
                            pool.submit(worker_extractor,
                                pcap_filepath,
                                temp_path,
                                (protocol, cmd_filter),
                                start_stream_id,
                                end_stream_id))

                    for task in concurrent.futures.as_completed(tasks):
                        _, temp_filepath = task.result()
                        merge_csv(
                            f"{temp_protocol_filename}.csv",
                            temp_filepath,
                            EXTRACT_PKT_PER_FLOW)


        with open(f"{export_filepath}.csv", "a") as f:
            f.write("time_epoch,frame_number,stream_id,ip_src,port_src,ip_dst,port_dst,ip_proto,protocol,length,info,data\n")

        merge_csv(f"{export_filepath}.csv", 
                  f"{temp_path}/tcp_{export_filename}.csv", 
                  EXTRACT_PKT_PER_FLOW)
        
        merge_csv(f"{export_filepath}.csv", 
                  f"{temp_path}/udp_{export_filename}.csv", 
                  EXTRACT_PKT_PER_FLOW)

        # Sorted by time_epoch
        pd.read_csv(f"{export_filepath}.csv").sort_values(by=["time_epoch"]).to_csv(
            f"{export_filepath}.csv", index=False
        )
        logging.debug(f'Sorted by time_epoch {export_filepath}.csv')
        
        # Remove nan value from dataframe
        pd.read_csv(f"{export_filepath}.csv").dropna().to_csv(
            f"{export_filepath}.csv", index=False
        )
        logging.debug(f'Drop nan value from {export_filepath}.csv')
        
        # Padding
        if HEX_TO_DEC:
            df = pd.read_csv(f"{export_filepath}.csv")
            int_payload = convert_to_int(df["data"])
            df = pd.concat([df, pd.DataFrame(int_payload)], axis=1)
            df.to_csv(f"{export_filepath}.csv", index=False)
            del df
        logging.info(
            f"Finised file {pcap_filepath} - Saved file: {export_filepath}.csv, Time taken: {time.time() - start_time}"
        )

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
        parser.add_argument("-so", "--sumary-only", default=0, type=int)
        parser.add_argument("-o", "--overide", default=0, type=int)
        args = parser.parse_args()

        EXTRACT_PKT_PER_FLOW = toml_dict["EXTRACT_PKT_PER_FLOW"]
        CONC_THREAD = toml_dict["CONC_THREAD"]

        OVERIDE = args.overide
        HEX_TO_DEC = toml_dict["HEX_TO_DEC"]
        PCAP_PATH = toml_dict["PCAP_PATH"]
        EXPORT_PATH = toml_dict["SAVED_PATH"]
        TEMP_PATH = toml_dict["TEMP_PATH"]

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
