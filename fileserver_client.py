import grpc
import file_server_pb2
import file_server_pb2_grpc
import logging
import os

def byteStream(uploadedFile):
    while True:
        data = uploadedFile.read(1)
        if data == "":
            break
        yield file_server_pb2.Chunk(chunk=data)

class Client:
    def __init__(self):
        logging.basicConfig()
        channel = grpc.insecure_channel('localhost:2750')
        self.stub = file_server_pb2_grpc.FileServiceStub(channel)
       

    def upload(self, uploadedFile):
        logging.info("within client upload")        
        bytearr = "SomeRandomStringForDemo".encode('ascii')
        chunks_generator = byteStream(uploadedFile)
        response = self.stub.Upload(chunks_generator)
        print(response.success)