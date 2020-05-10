import grpc
import file_server_pb2
import file_server_pb2_grpc
import logging
import os

CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB

class Client:
    def __init__(self):
        logging.basicConfig()
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
        logging.info("within client upload")        
        chunks_generator = self._byteStream(uploadedFile)
        metadata = (('filename', uploadedFile.filename),)
        response = self.stub.Upload(chunks_generator, metadata=metadata)
        return response.success