# CMPE 275(Enterprise Application Development)

## System Design

![System Design](https://github.com/priyakhadke15/dataverseproject/blob/master/system_design.png)

## Team Members
1. [Priya Khadke](https://github.com/priyakhadke15)
2. [Harshada Jivane](https://github.com/HarshadaJiv)
3. [Manasa Hari](https://github.com/harimanasa)
4. [Ankit Thanekar](http://www.github.com/ankit-thanekar007)
5. [Shailesh Nayak](https://github.com/shailesh-nyk)

## Configuration

### Setting Up Amazon S3 bucket
```
https://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html
```

### In grpc_server.py Update these values :
```
  1. bucket_name : Name of you Amazon S3 bucket
  2. AWS_ACCESS_KEY_ID : AWS Access Key 
  3. AWS_SECRET_ACCESS_KEY : AWS SECRET ACCESS KEY

https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey
```

## Installation Steps

### Install python virtual env:
```
  1.  python -m pip install virtualenv
  2.  virtualenv venv
  3.  source venv/bin/activate
  4.  python -m pip install --upgrade pip
```

### Package Installation
```
pip install -r requirements.txt
```

### Generate GRPC server files
```
1. cd project home dir
2. python -m grpc_tools.protoc -I ./protos --python_out=./runtime --grpc_python_out=./runtime ./protos/file_server.proto
```
### Run 
```
1. cd project home dir/serviceRegistry
2. python serviceRegistry.py
3. cd project home dir/application_server
4. python server.py
5. cd project home dir/grpc_server
6. In new terminals run multiple GRPC servers using IPaddress and port number in args 
   python grpc_server.py 127.0.0.1 2750
   python grpc_server.py 127.0.0.1 2751 
```
### Performance Results
 ## Upload Request Times 
![Upload Request Times](https://github.com/priyakhadke15/dataverseproject/blob/master/uploadtimes.png)

 ## Download Request Times 
![Upload Request Times](https://github.com/priyakhadke15/dataverseproject/blob/master/downloadtimes.png)

## Reference
- https://ops.tips/blog/sending-files-via-grpc/
- https://grpc.io/docs/tutorials/basic/python/
- https://www.nginx.com/blog/service-discovery-in-a-microservices-architecture/
