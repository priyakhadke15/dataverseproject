import grpc
import file_server_pb2
import file_server_pb2_grpc
import logging
import os

CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_FOLDER = '{}/downloads/'.format(PROJECT_HOME)

class Client:
    def __init__(self):
        logging.basicConfig()
        logging.info("initializing GRPC client")
        channel = grpc.insecure_channel('localhost:2750')
        self.stub = file_server_pb2_grpc.FileServiceStub(channel)

    def _byteStream(self,fileHandle):
        while True:
            chunk = fileHandle.read(CHUNK_SIZE)
            if not chunk:
                fileHandle.close()
                break
            yield file_server_pb2.Chunk(chunk=chunk)

    def upload(self, uploadedFile):
        print("within GRPC client upload")        
        chunks_generator = self._byteStream(uploadedFile)
        metadata = (('filename', uploadedFile.filename),)
        response = self.stub.Upload(chunks_generator, metadata=metadata)
        return response.success

    def download(self, filename):
        print("within GRPC client download")   
        response = self.stub.Download(file_server_pb2.Name(name=filename))
        fileHandle = open(os.path.join(DOWNLOAD_FOLDER, filename), "wb")
        if fileHandle is not None:
            for chunk in response:
                fileHandle.write(chunk.chunk)
            fileHandle.close()
            return True
        return False