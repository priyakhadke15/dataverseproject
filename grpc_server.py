from concurrent import futures
import threading
import grpc
import file_server_pb2
import file_server_pb2_grpc
import time

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

# FileServiceServicer provides an implementation of the methods of the FileServer service.
class FileServicer(file_server_pb2_grpc.FileServiceServicer):
    def __init__(self):
        print('initialization')

    def Upload(self, request, context):
        print('in upload')
        for c in request:
            print(c)
        return file_server_pb2.UploadStatus(success=False)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_server_pb2_grpc.add_FileServiceServicer_to_server(FileServicer(), server)
    server.add_insecure_port('[::]:2750')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()