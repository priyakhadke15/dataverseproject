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
2. python -m grpc_tools.protoc -I ./protos --python_out=. --grpc_python_out=. ./protos/file_server.proto
```

## Reference
https://ops.tips/blog/sending-files-via-grpc/
https://grpc.io/docs/tutorials/basic/python/