import os, sys, logging
import subprocess
import re, functools
import numpy as np
import pandas as pd

def ls_file_in_current_folder(path) -> list[str]:
    return [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]

def ls_folder_in_current_folder(path) -> list[str]:
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def mkpath_abs(path) -> str:
    # return os.path.abspath(os.path.expanduser(path))
    if not os.path.isabs(path):
        path = os.path.abspath(os.path.expanduser(path))
    return path

def mkdir_by_path(path) -> None:
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f'Created directory: {path}')
    except NotADirectoryError:
        logging.error(f'Not a directory: {path} or already exists as a file')

def touch_file_by_path(path):
    pass

def ls_subfolders(rootdir) -> list[str]:
    sub_folders_n_files = []
    for path, _, files in os.walk(rootdir):
        for name in files:
            sub_folders_n_files.append(os.path.join(path, name))
    return sorted(sub_folders_n_files)

def ls_protocol(file):
    result, err = subprocess.Popen(
        f"tshark  -r {file} -qz io,phs",
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
    ).communicate()
    decode_output = result.decode("latin-1")

    if len(re.findall("tcp", decode_output)) > 0:
        tcp = True

    if len(re.findall("udp", decode_output)) > 0:
        udp = True
    logging.debug(f"TCP stream len: {tcp}, UDP stream len: {udp}")
    return [tcp, udp]

def convert_to_int(datas) -> list[int]:
    array = []
    for data in datas:
        if len(re.findall(":", data)) > 0:
            split_data = data.split(":")
        else:
            split_data = re.findall(".{1,2}", data)

        int_payload = list(map(functools.partial(int, base=16), split_data))
        int_payload = int_payload[0:1460]
        int_payload_pad = np.pad(
        
            int_payload,
            (0, 1460 - len(int_payload)),
            "constant",
            constant_values=(0, 0),
        )
        array.append(int_payload_pad)
    return array

def merge_csv(root_file: str, temp_file: str, extract_pkt_per_flow: int=0) -> str:
    if os.path.isfile(temp_file):
        if os.stat(temp_file).st_size != 0:
            df = pd.read_csv(
                temp_file,
                header=None,
                on_bad_lines="skip",
                encoding="latin-1",
                engine="python",
            )
            if extract_pkt_per_flow > 0: 
                df.groupby(2).head(extract_pkt_per_flow).to_csv(
                    temp_file, mode="w", chunksize=128, header=False, index=False
                )
            subprocess.Popen(f"cat {temp_file} >> {root_file}", shell=True).wait()
            logging.debug(f"Merge {temp_file} to {root_file}")
        os.remove(temp_file)
        logging.debug(f"Remove {temp_file}")
    return root_file

def stream_id_spliter(stream_id_len, filesize) -> list[list[int]]:
    if filesize <= 700:
        if stream_id_len < 50:
            n_split = 1
        if stream_id_len >= 50:
            n_split = 5
        if stream_id_len >= 500:
            n_split = 15
        if stream_id_len > 5000:
            n_split = 50 + int(stream_id_len * 0.005)
    if filesize > 700:
        if stream_id_len < 10:
            n_split = 1
        if stream_id_len >= 10:
            n_split = 4
        if stream_id_len >= 50:
            n_split = 10
        if stream_id_len >= 100:
            n_split = 25
        if stream_id_len >= 500:
            n_split = 30 + int(stream_id_len * 0.001)
        if stream_id_len > 5000:
            n_split = 40 + int(stream_id_len * 0.0015)
    a = np.array_split(range(stream_id_len), n_split)
    return [[i[0], i[-1]] for i in a]

def stream_id_len(filename, export_summary_filename):
    result_tcp, _ = subprocess.Popen(
        f'tshark -r "{filename}" -qz conv,tcp',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    result_udp, _ = subprocess.Popen(
        f'tshark -r "{filename}" -qz conv,udp',
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).communicate()

    start_index_report = [i for i, s in enumerate(
        result_tcp.decode("latin-1").split("\n")
        ) if "Frames  Bytes" in s][0]
    
    start_index_report += 2

    tcp_stream_count = (
        result_tcp.decode("latin-1").split("\n").__len__() - start_index_report - 1
    )
    udp_stream_count = (
        result_udp.decode("latin-1").split("\n").__len__() - start_index_report - 1
    )

    result_tcp = result_tcp.decode("latin-1").split("\n")[start_index_report - 1 : -2]
    result_udp = result_udp.decode("latin-1").split("\n")[start_index_report - 1 : -2]

    with open(f"{export_summary_filename}_summary.csv", "w") as txt_file:
        txt_file.write(
            "l4_proto;A,B,A<-B_frame;A<-B_byte;A->B_frame;A->B_byte;total_frame;total_byte;relative_start;duration\n")
        for result in result_tcp:
            result = [x for x in result.split(" ") if x != ""]
            line = f'tcp;{result[0]};{result[2]};{result[3]};{result[4]} {result[5]};{result[6]};{result[7]} {result[8]};{result[9]};{result[10]} {result[11]};{result[12]};{result[13]}'
            txt_file.write(f"{line}\n")
        for result in result_udp:
            result = [x for x in result.split(" ") if x != ""]
            line = f'udp;{result[0]};{result[2]};{result[3]};{result[4]} {result[5]};{result[6]};{result[7]} {result[8]};{result[9]};{result[10]} {result[11]};{result[12]};{result[13]}'
            txt_file.write(f"{line}\n")
    return tcp_stream_count, udp_stream_count

def worker_extractor(pcap_filepath: str, temp_path: str, 
                     protocol_filter: tuple(), 
                     start_stream_id: int, end_stream_id: int):

    protocol = protocol_filter[0]
    cmd_filter = protocol_filter[1]

    temp_filename = f"{temp_path}/{protocol}_{start_stream_id}_{end_stream_id}.csv"
    cmd =(f"""tshark -r "{pcap_filepath}" \
              {cmd_filter.format(start_stream_id=start_stream_id, end_stream_id=end_stream_id)} \
              >> "{temp_filename}" """)

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result, error = proc.communicate()
    logging.debug(f'tshark extract result: {result.decode("latin-1")}, err: {error.decode("latin-1")} on {pcap_filepath}')
    logging.info(f'Extracted temp part {protocol}: {start_stream_id} to {end_stream_id} to {temp_filename}')
    return [start_stream_id, end_stream_id], temp_filename


def worker_summary(filepath: str, export_summary_filename: str):
    stream_id_len(filepath, export_summary_filename)
    return filepath, export_summary_filename