from concurrent import futures
import threading
import grpc
import file_server_pb2
import file_server_pb2_grpc
import time
import os,logging


_ONE_DAY_IN_SECONDS = 60 * 60 * 24
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)
CHUNK_SIZE = int(1024 * 1024 * 3.9) # 3.99MB

# FileServiceServicer provides an implementation of the methods of the FileServer service.
class FileServicer(file_server_pb2_grpc.FileServiceServicer):
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        logging.info('initializing GRPC server')

    def Upload(self, request, context):
        metadata = context.invocation_metadata()
        filename = 'output'
        for c in metadata:
            if(c.key == 'filename'):
                filename = c.value
                break
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as output:
                for c in request:
                    # print(c)
                    output.write(c.chunk)
            output.close()
            return file_server_pb2.UploadStatus(success=True)
        except Exception, e:
            logging.warning('Failed to upload to ftp: '+ str(e))
            return file_server_pb2.UploadStatus(success=False)
    
    def _byteStream(self, fileHandle):
        while True:
            chunk = fileHandle.read(CHUNK_SIZE)
            if not chunk:
                fileHandle.close()
                break
            yield file_server_pb2.Chunk(chunk=chunk)

    def Download(self, request, context):
        try:
            filename = request.name
            logging.info(request.name)
            logging.info('Starting GRPC download')
            fileHandle = open(os.path.join(UPLOAD_FOLDER, filename), "rb")
            logging.info('completed GRPC download')
            return self._byteStream(fileHandle)
        except Exception,e:
            logging.warning('Failed GRPC download : '+ str(e))
            return None
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_server_pb2_grpc.add_FileServiceServicer_to_server(FileServicer(), server)
    server.add_insecure_port('[::]:2750')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()