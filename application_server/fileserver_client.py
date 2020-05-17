import grpc
import logging
import os
import random
import sys

sys.path.append('../')
import file_server_pb2
import file_server_pb2_grpc

CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_FOLDER = '{}/downloads/'.format(PROJECT_HOME)

class Client:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        logging.info("initializing GRPC client")
        
    def _byteStream(self,fileHandle):
        while True:
            chunk = fileHandle.read(CHUNK_SIZE)
            if not chunk:
                fileHandle.close()
                break
            yield file_server_pb2.Chunk(chunk=chunk)

    def _createFolder(self):
        if not os.path.exists(DOWNLOAD_FOLDER):
            os.makedirs(DOWNLOAD_FOLDER)
            logging.info("created /downloads folder")
        else:
            logging.info("/downloads folder exists")
        logging.info(DOWNLOAD_FOLDER)  
    
    def upload(self, uploadedFile, grpcServerIP):
        logging.info("within GRPC client upload")  
        try:
            stub=self._connect(grpcServerIP)
            chunks_generator = self._byteStream(uploadedFile)
            metadata = (('filename', uploadedFile.filename),)
            response = stub.Upload(chunks_generator, metadata=metadata)
            return response.success
        except Exception as e:
            logging.warning("%s",str(e))

    def download(self, filename, grpcServerIP):
        logging.info("within GRPC client download")
        try:
            stub=self._connect(grpcServerIP)
            response = stub.Download(file_server_pb2.Name(name=filename))
            logging.info(response)
            self._createFolder()
            fileHandle = open(os.path.join(DOWNLOAD_FOLDER, filename), "wb")
            if fileHandle is not None:
                for chunk in response:
                    fileHandle.write(chunk.chunk)
                fileHandle.close()
                logging.info("Exiting GRPC client download")
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