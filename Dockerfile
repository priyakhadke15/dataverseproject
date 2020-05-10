FROM python:2.7.18-slim-stretch
COPY . /usr/local/dataverse
WORKDIR /usr/local/dataverse
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "grpc_server.py"]
