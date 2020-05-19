from concurrent import futures
# import threading
import grpc
import time
import os,logging,sys
import requests
import boto3
from botocore.exceptions import NoCredentialsError,ClientError

sys.path.append('../runtime/')

import file_server_pb2
import file_server_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB
serviceRegistry_url = 'http://127.0.0.1:5001'
thisnodeAdd = {'ipaddress': sys.argv[1],
               'port': sys.argv[2], 
              }
bucket_name ='dataverse-cmpe275'
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = 'H'
            
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

            try:
                s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                print(str(s3))
                print(request)
                s3.upload_file(os.path.join(UPLOAD_FOLDER,filename), bucket_name, filename)    
                print("S3 Upload Successful")
                return file_server_pb2.UploadStatus(success=True)
            except Exception:
                print("S3 not available, File uploaded to Uploads only not on S3")
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
            ifexist=os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)) 
            if ifexist:
                print("File Cached, Fetching file from cache")
                fileHandle = open(os.path.join(UPLOAD_FOLDER, filename), "rb")
                return self._byteStream(fileHandle)
            elif not ifexist:
                try:
                    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                    s3.head_object(Bucket=bucket_name, Key=filename)
                except ClientError as e:
                    print("Exception "+e)
                    if e.response['Error']['Code'] == "404":
                         print(filename+" does not exists on Cache and S3")
                         return  None
                print("File Not Cached, Fetching file from S3")
                s3.download_file(bucket_name,filename,os.path.join(UPLOAD_FOLDER,filename))
                fileHandle = open(os.path.join(UPLOAD_FOLDER, filename), "rb")
                print("Fetching from S3 completed")
                return self._byteStream(fileHandle)

            logging.info('Completed GRPC download')
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
