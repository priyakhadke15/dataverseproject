import grpc
import file_server_pb2
import file_server_pb2_grpc
# import io
# import hashlib
# import math
# import sys
# import os
# import funcy
# import uuid
import logging

CHUNK_SIZE = 1024 * 1024 * 3  # 3MB
NO_OF_CHUNKS = 0

def byteStream(arr):
    for b in arr:
        yield file_server_pb2.Chunk(chunk=b)

def run():
    channel = grpc.insecure_channel('localhost:2750')
    stub = file_server_pb2_grpc.FileServiceStub(channel)
    bytearr = "someStringDKJDKJlsdjalkdsjfklsd".encode('ascii')
    chunks_generator = byteStream(bytearr)
    response = stub.Upload(chunks_generator)
    print(response.success)
    
if __name__ == '__main__':
    logging.basicConfig()
    run()