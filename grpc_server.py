from concurrent import futures
import threading
import grpc
import file_server_pb2
import file_server_pb2_grpc
import time
import os

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)

# FileServiceServicer provides an implementation of the methods of the FileServer service.
class FileServicer(file_server_pb2_grpc.FileServiceServicer):
    def __init__(self):
        print('initialization')

    def Upload(self, request, context):
        metadata = context.invocation_metadata()
        # print(metadata)
        filename = 'output'
        for c in metadata:
            if(c.key == 'filename'):
                filename = c.value
                break
        print(filename)
        try:
            with open(os.path.join(UPLOAD_FOLDER, filename), "wb") as output:
                for c in request:
                    # print(c)
                    output.write(c.chunk)
            output.close()        
            return file_server_pb2.UploadStatus(success=True)
        except Exception, e:
            print('Failed to upload to ftp: '+ str(e))
            return file_server_pb2.UploadStatus(success=False)
        
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_server_pb2_grpc.add_FileServiceServicer_to_server(FileServicer(), server)
    server.add_insecure_port('[::]:2750')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()