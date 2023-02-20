import os, sys
import subprocess
import fastapi  
'''
    This script is used to play pcap files on a mininet network
    Meant to be used in mininet hosts
'''

os.putenv()

from typing import Union

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# def main():
#     pass

# if __name__ == main():
#     try:
#         main()
#     except KeyboardInterrupt:
#         print('Interrupted')
#         try:
#             sys.exit(0)
#         except SystemExit:
#             os._exit(0)
