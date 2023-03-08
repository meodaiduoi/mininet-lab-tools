from pydantic import BaseModel
import uvicorn

from pathlib import Path
from fastapi import FastAPI
from fastapi import Request, Response

from fastapi import File, UploadFile
from fastapi.responses import FileResponse

import os, sys, subprocess, argparse
import logging
import datetime, time
import threading

import requests as rq

app = FastAPI()

class HostTask(BaseModel):
    ip: str
    port: int
    filesize: int | None = None

def generate_big_file(filename, size=100):
    '''
        Create random file with name and
        size in unit MB
    '''
    with open(f'{filename}', 'wb') as f:
        f.seek(1024 * 1024 * size -1)
        f.write(str.encode("0"))

# Client
@app.post('/upload_speed/')
async def upload_speed(url, size=100):
    '''
        url with default upload size = 100mb
        filename id is unix time
        speed unit: Mbit/s
    '''
    id_filename = str(int(time.time()*10**6))
    filename = f'temp/{id_filename}'
    generate_big_file(filename, size)
    with open(f'{filename}', 'r') as upload_file:
        start_time = time.time()
        respone = rq.post(url, files={'file': upload_file})
        end_time = time.time()
    os.remove(filename)
    
    speed = -1
    if respone.status_code == 200:
        speed = size*8 / (end_time - start_time)
        speed = round(speed, 5)
    return {'upload_speed': speed}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    id_filename = str(int(time.time()*10**6))
    file_path = f'temp/{id_filename}'

    try:
        contents = await file.read()
        with open('test', 'wb') as f:
            f.write(file_path)
    except Exception:
        return {"message": "There was an error uploarding the file"}
    finally:
        await file.close()
    
    task = threading.Thread(target=remove_file_after_download, args=(file_path, 1))
    task.daemon = True
    task.start()

    return {"message": f"Successfuly uploaded {file.filename}"}

@app.post('/download_speed/')
async def download_file(url, size=100):
    '''
        url with default download size = 100mb
        filename id is unix time
        speed unit: Mbit/s
    '''
    id_filename = str(int(time.time()*10**6))
    filename = f'temp/{id_filename}'
    with rq.get(url, stream=True) as respone:
        start_time = time.time()
        respone.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in respone.iter_content(chunk_size=8192): 
                f.write(chunk)
        end_time = time.time()
        
        speed = -1
        if respone.status_code == 200:
            size = os.path.getsize(filename)
            speed = size/1024/1024*8 / (end_time - start_time)
            speed = round(speed, 5)
        os.remove(filename)
    return {'download_speed': speed}

@app.get('/download/{size}')
async def download_file_with_size(size: int):
    id_filename = str(int(time.time()*10**6))
    file_path = f'temp/{id_filename}'
    generate_big_file(file_path, size)
    
    task = threading.Thread(target=remove_file_after_download, args=(file_path,))
    task.daemon = True
    task.start()

    return FileResponse(path=file_path, filename=file_path); 


@app.get('/respone_time')
async def get_server_respone_time():
    return {'time': int(time.time() * 1000)}

@app.post('/respone_time')
async def post_server_respone_time():
    client_send_time = int (time.time() * 1000)
    respone = rq.get('http://10.0.0.2:8000/respone_time')
    server_recive_time = int(respone.json()['time'])
    client_recive_time = int (time.time() * 1000)
    rsp_time =  (server_recive_time - client_send_time) + (client_recive_time - server_recive_time) 
    print(rsp_time)
    return {'time': rsp_time} 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='simple cli client')
    
    parser.add_argument('ip', type=str,
                        default='0.0.0.0',
                        help='ip address of server')
    
    parser.add_argument('port', type=int,
                        default=8000,
                        help='port of server')

    args = parser.parse_args()
    
    # Create logger
    if 
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

