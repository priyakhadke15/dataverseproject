import grpc
import file_server_pb2
import file_server_pb2_grpc
import logging
import os
import commands
import random

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

    def upload(self, uploadedFile):
        
        logging.info("within GRPC client upload")  
        try:
            stub=self._connect()
            chunks_generator = self._byteStream(uploadedFile)
            metadata = (('filename', uploadedFile.filename),)
            response = stub.Upload(chunks_generator, metadata=metadata)
            return response.success
        except Exception as e:
            logging.warning("%s",str(e))

    def download(self, filename):
        logging.info("within GRPC client download")
        try:
            stub=self._connect()
            response = stub.Download(file_server_pb2.Name(name=filename))
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
    
    # Gets the list of GRPC Servers ports running as
    def _getAllNodes(self):
        list_of_ps = os.popen("ps -eaf|grep grpc_server").read().split('\n')
        output = [i for i in list_of_ps if "python" in i]
        i=0
        portList =[]
        while i<len(output):
            temp = output[i].split(' ')
            portList.append(temp[len(temp)-1])
            logging.info("GRPC servers on port %s",str(temp[len(temp)-1]))
            i=i+1
        return portList
    
    # connect to given GRPC server
    def _connect(self):
        # Move the host selection logic next 2 lines to Consistent Hash algorithm
        ports = self._getAllNodes()
        portNumber=random.choice(ports)
        channel = grpc.insecure_channel('localhost:'+portNumber)
        stub = file_server_pb2_grpc.FileServiceStub(channel)
        return stub