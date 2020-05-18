import grpc
import logging
import os
import random
import sys

sys.path.append('../runtime')
import file_server_pb2
import file_server_pb2_grpc

CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB

class Client:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("initializing GRPC client")

    def _byteStream(self, fileHandle):
        while True:
            chunk = fileHandle.read(CHUNK_SIZE)
            if not chunk:
                break
            yield file_server_pb2.Chunk(chunk=chunk)
    
    def upload(self, uploadedFile, grpcServerIP, chunkName):
        logging.info("within GRPC client upload")  
        try:
            stub=self._connect(grpcServerIP)
            chunks_generator = self._byteStream(uploadedFile)
            metadata = (('filename', chunkName),)
            response = stub.Upload(chunks_generator, metadata=metadata)
            return response.success
        except Exception as e:
            logging.warning("%s",str(e))

    def download(self, filename, grpcServerIP, fileHandle):
        logging.info("within GRPC client download")
        try:
            stub=self._connect(grpcServerIP)
            response = stub.Download(file_server_pb2.Name(name=filename))
            if fileHandle is not None:
                for chunk in response:
                    fileHandle.write(chunk.chunk)
                logging.info("Successfully downloaded chunk %s Exiting GRPC client download", filename)
                return True
            logging.warning("GRPC client fail download")    
            return False
        except Exception as e:
            logging.warning("%s",str(e))
            return False
    
    # connect to given GRPC server
    def _connect(self, grpcServerIP):
        logging.info("connecting to grpc server at %s", grpcServerIP)
        channel = grpc.insecure_channel(grpcServerIP)
        stub = file_server_pb2_grpc.FileServiceStub(channel)
        return stub
