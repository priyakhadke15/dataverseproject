from concurrent import futures
# import threading
import grpc
import time
import os,logging,sys
import requests

sys.path.append('../runtime')
import file_server_pb2
import file_server_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB
serviceRegistry_url = 'http://0.0.0.0:5001'
thisnodeAdd = {'ipaddress': sys.argv[1],
               'port': sys.argv[2], 
              }
            
# FileServiceServicer provides an implementation of the methods of the FileServer service.
class FileServicer(file_server_pb2_grpc.FileServiceServicer):
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        logging.info('initializing GRPC server')
        try:
            registerAPI = serviceRegistry_url+"/register"
            x = requests.post(registerAPI, data = thisnodeAdd)
        except Exception as e:
            logging.warning('Failed to register: '+ str(e))

    def Upload(self, request, context):    
        try:
            metadata = context.invocation_metadata()
            filename = None
            for c in metadata:
                if(c.key == 'filename'):
                    filename = c.value
                    break
            self._createFolder()
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as output:
                for c in request:
                    output.write(c.chunk)
            output.close()
            return file_server_pb2.UploadStatus(success=True)
        except Exception as e:
            logging.warning('Failed to upload to ftp: '+ str(e))
            return file_server_pb2.UploadStatus(success=False)
    
    def _byteStream(self, fileHandle):
        logging.info('\nin bytestream\n')
        while True:
            chunk = fileHandle.read(CHUNK_SIZE)
            if not chunk:
                fileHandle.close()
                break
            yield file_server_pb2.Chunk(chunk=chunk)

    def Download(self, request, context):
        print('in download')
        logging.info('in download')
        try:
            filename = request.name
            logging.info(request.name)
            print(filename)
            logging.info('Starting GRPC download')
            fileHandle = open(os.path.join(UPLOAD_FOLDER, filename), "rb")
            logging.info('completed GRPC download')
            return self._byteStream(fileHandle)
        except Exception as e:
            logging.info('Failed GRPC download : '+ str(e))
            logging.warning('Failed GRPC download : '+ str(e))
            print('Failed GRPC download : '+ str(e))
            return None

    def _createFolder(self):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
            logging.info("created uploads folder")
        else:
            logging.info("uploads folder exists")
        logging.info(UPLOAD_FOLDER)    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_server_pb2_grpc.add_FileServiceServicer_to_server(FileServicer(), server)
    logging.info('Starting GRPC server on port :%s',str(sys.argv[2]))
    port=str(sys.argv[2])
    # change ipaddress logic here
    server.add_insecure_port('[::]:'+port)
    server.start()
    starttime=time.time()
    heartbeatAPI = serviceRegistry_url+"/heartbeat"
    while True:
        logging.info('sending heartbeat at %s', heartbeatAPI)
        requests.put(heartbeatAPI, data = thisnodeAdd)
        time.sleep(10)
    server.wait_for_termination()

if __name__ == '__main__':
    serve()