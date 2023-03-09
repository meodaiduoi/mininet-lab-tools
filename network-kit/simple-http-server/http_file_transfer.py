from pydantic import BaseModel
import uvicorn

from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response

from fastapi import File, UploadFile
from fastapi.responses import FileResponse

import os, sys, argparse
import logging, tomli
import datetime, time

import json
import requests as rq

app = FastAPI()

# Utility functions
def generate_big_file(filename, size=100) -> str:
    '''
        Create random file with name and
        size in unit MB
    '''
    file_path = f'temp/{filename}'
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(f'{file_path}', 'wb') as f:
        f.seek(1024 * 1024 * size -1)
        f.write(str.encode("0"))
    return file_path

def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

# API functions
class FileTask(BaseModel):
    ip: str
    port: int
    size: int | None = 100 # MByte

class RemoveFileTask(BaseModel):
    file_path: str

@app.post('/remove_file/')
async def remove_file(rm_task: RemoveFileTask):
    file_path = rm_task.file_path
    if os.path.exists(file_path):
        os.remove(file_path)

@app.post('/upload_speed/')
async def upload_speed(upload_task: FileTask):
    '''
        url with default upload size = 100mb
        filename id is unix time
        speed unit: Mbit/s
    '''
    filename = time.time_ns()
    file_path = generate_big_file(filename, upload_task.size)
    with open(f'{file_path}', 'r') as upload_file:
        start_time = time.time()
        respone = rq.post(f'http://{upload_task.ip}:{upload_task.port}/upload', 
                          files={'file': upload_file})
        end_time = time.time()
    os.remove(file_path)
    
    speed = -1
    if respone.status_code == 200:
        speed = upload_task.size*8 / (end_time - start_time)
        speed = round(speed, 5)
    # Upload speed is in Mbit/s
    return Response(status_code=200, content={"upload_speed": speed})

# @app.post("/upload")
# async def upload(file: UploadFile = File(...)):
    
#     file_path = f'temp/{file.filename}'

#     try:
#         contents = await file.read()
#         with open('test', 'wb') as f:
#             f.write(file_path)
#     except Exception:
#         return {"message": "There was an error uploarding the file"}
#     finally:
#         await file.close()
#         os.remove(file_path)
#     return {"message": f"Successfuly uploaded {file.filename}"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_path = f'temp/{file.filename}'
    with open(file_path, 'wb') as f:
        contents = await file.read()
        f.write(contents)
    return {"message": f"Successfuly uploaded {file.filename}"}


@app.post('/download_speed/')
async def download_speed(download_task: FileTask):
    '''
        url with default download size = 100mb
        filename id is unix time
        speed unit: Mbit/s
    '''
    filename = time.time_ns()
    file_path = f'temp/{filename}'
    
    with rq.get(f'http://{download_task.ip}:{download_task.port}/download/{download_task.size}', stream=True) as respone:
        start_time = time.time()
        respone.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in respone.iter_content(chunk_size=8192): 
                f.write(chunk)
        end_time = time.time()
        
        speed = -1
        if respone.status_code == 200:
            size = os.path.getsize(file_path)
            speed = size/1024/1024*8 / (end_time - start_time)
            speed = round(speed, 5)
        os.remove(file_path)
    rq.post(f'http://{download_task.ip}:{download_task.port}/remove_file', json=json.dumps({'file_path': filename}))
    return Response(status_code=200, content={"download_speed": speed})

@app.get('/download/{size}')
async def download(size: int=100):
    filename = time.time_ns()
    file_path = generate_big_file(filename, size)
    return FileResponse(path=file_path, filename=file_path); 

class ResponeTimeTask(BaseModel):
    ip: str
    port: int | None = 8000

@app.post('/respone_time')
async def server_respone_time(rpt_task: ResponeTimeTask):
    '''
        Step 1: client send request to server with time
        Step 2: server recive request and send response with time
        Step 3: client recive response and calculate time
        return server time in milisecond
    '''
    cl_current_time = time.time_ns()
    data = {
        'cl_current_time': cl_current_time
    }
    sv_data = rq.post(f'http://{rpt_task.ip}:{rpt_task.port}/sv_respone_time', json=json.dumps(data)).json()
    cl_to_sv = sv_data['cl_to_sv']
    sv_current_time = sv_data['sv_current_time']
    result_time = time.time_ns() - sv_current_time + cl_to_sv
    
    # return in milisecond
    return Response(status_code=200, 
                    content=json.dumps({"time": result_time/10**6}))

class ResponeTimeChainTask(BaseModel):
    cl_current_time: int

@app.post('/sv_respone_time')
async def post_server_respone_time(rp_time: ResponeTimeChainTask):
    sv_current_time = time.time_ns()
    cl_to_sv_latency = time.time_ns() - rp_time.cl_current_time
    return Response(status_code=200, 
                    content=json.dumps({"cl_to_sv": cl_to_sv_latency,
                                        'sv_current_time': sv_current_time}))

def main():
    parser = argparse.ArgumentParser(description='simple cli client')
    
    parser.add_argument('ip', type=str,
                        default='0.0.0.0',
                        help='ip address of server')
    
    parser.add_argument('port', type=int,
                        default=8000,
                        help='port of server')
    args = parser.parse_args()

    # import config.toml
    # try:
    #     with open('config.toml', 'r') as f:
    #         config = tomli.load(f)
    #     mkdir(config['log_path'])
    # except FileNotFoundError:
    #     print('config.toml not found')
    #     sys.exit(1)

    # Create folder for temp file
    mkdir('temp')
    mkdir('log')

    # Create logger
    file_handler = logging.FileHandler(
        filename=f'log/{args.ip}_{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.log')
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
        handlers=handlers
    )

    uvicorn.run(app, host=args.ip, port=args.port)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
