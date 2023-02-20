#!/home/onos/Documents/Github/venv10/bin/python3

'''
    This script is used to play pcap files on a mininet network
    Meant to be used in mininet hosts
'''

import os, sys
import subprocess
import fastapi  

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from threading import Thread
import uvicorn

class ServicePcap(BaseModel):
    service_name: str
    pcap_file: str
    src_name: str
    # src_ip: str
    dst_name: str
    # dst_ip: str

# '''
#     {[{host_name: ip}, {host_name: ip},...]}
# '''

# class HostsIps(BaseModel):
#     hosts_ips: list

def ls_subfolders(rootdir):
    sub_folders_n_files = []
    for path, _, files in os.walk(rootdir):
        for name in files:
            sub_folders_n_files.append(os.path.join(path, name))
    return sorted(sub_folders_n_files)

# split folder
fd = ls_subfolders('/home/onos/Desktop/output_rewrite/')
folders = [os.path.split(f)[0] for f in fd]
files = [os.path.split(f)[1] for f in fd]

def ls_subfolders(rootdir):
    sub_folders_n_files = []
    for path, _, files in os.walk(rootdir):
        for name in files:
            sub_folders_n_files.append(os.path.join(path, name))
    return sorted(sub_folders_n_files)

app = FastAPI()

# @app.get("/")
# def read_root():
    # return {"Hello": "World"}

# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
    # return {"item_id": item_id, "q": q}

# @app.post("/update_ip_index")
# def update_ip_index(ip_index: HostsIps):
    # return ip_index

@app.post("/play_pcap")
async def play_pcap(service_pcap: ServicePcap):
    store_path = '/home/onos/Desktop/output_rewrite/'    
    file_path = f'{store_path}{service_pcap.service_name}/{service_pcap.pcap_file}/{service_pcap.src_name}-{service_pcap.dst_name}/{service_pcap.src_name}-{service_pcap.dst_name}.pcap'    

    result = subprocess.Popen(f'echo "rocks" | sudo -S -k tcpdump -i ens33 -K {file_path}', shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return {
        'result': result[0],
        'error': result[1]
    }

class RespondingTime(BaseModel):
    end_time: float

@app.post("/responding_time")
async def responding_time(end_time: RespondingTime):
    return {
        'end_time': end_time.end_time
    }

@app.get('/')
async def hello():
    return {
        'hello': 'world'
    }

# @app.post("/")
# def update_route():
#     return {""}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
