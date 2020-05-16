# CMPE 275(Enterprise Application Development)

## Installation Steps

### Install python virtual env:
```
  1.  python -m pip install virtualenv
  2.  virtualenv venv
  3.  source venv/bin/activate
  4.  python -m pip install --upgrade pip
```

### Package Installation
pip install -r requirements.txt

### Generate GRPC server files
```
1. cd project home dir
2. python -m grpc_tools.protoc -I ./protos --python_out=./runtime --grpc_python_out=./runtime ./protos/file_server.proto
```
### Run 
```
1. python application_server/server.py
2. In new terminals run multiple GRPC servers using IPaddress and port number in args 
   python grpc_server/grpc_server.py 127.0.0.0 2750
   python grpc_server/grpc_server.py 127.0.0.0 2751
```
## Reference
https://ops.tips/blog/sending-files-via-grpc/
https://grpc.io/docs/tutorials/basic/python/
https://www.nginx.com/blog/service-discovery-in-a-microservices-architecture/