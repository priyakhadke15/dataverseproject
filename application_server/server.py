from flask import Flask,request,jsonify, make_response,send_file
from werkzeug.utils import secure_filename
import logging,os
import sys
import time
import hashlib
import requests
import threading
import json
from io import BytesIO
from flask_cors import CORS

sys.path.append('../runtime')
import fileserver_client

app = Flask(__name__)
app.logger.setLevel(logging.INFO)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_FOLDER = '{}/downloads/'.format(PROJECT_HOME)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF","TXT","DOC","DOCX","PDF","MKV","AVI","DIVX","MP4"]
SERVICE_REGISTRY_URL = 'http://ec2-3-82-108-99.compute-1.amazonaws.com:5001'
MAX_FILE_SIZE = int(1024 * 1024 * 30) # 30MB

@app.route("/")
def index():
    return "Test Route!"

@app.route("/upload", methods = ['POST'])
def upload():
    if request.files['file']:
        try:
            uploadedFile = request.files['file']
            if not "." in uploadedFile.filename:
                app.logger.info("uploaded filename:", uploadedFile.filename)
                return make_response(jsonify({"msg":"invalid file name"}),400)

            ext = uploadedFile.filename.rsplit(".", 1)[1]
            if ext.upper() not in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                 return make_response(jsonify({"msg":"invalid file extension"}),400)

            start = time.time()
            runningMD5 = hashlib.md5()
            chunks = []
            threads = []
            chunkCtr = 1
            prevReadPtr = 0
            totalFileSize = 0
            while True:
                chunk = uploadedFile.read(MAX_FILE_SIZE)
                if not chunk:
                    break
                chunkmd5 = hashlib.md5(chunk).hexdigest()
                runningMD5.update(chunk)

                threads.append(threading.Thread(target=__uploadChunk, args=(chunk, chunkmd5,),))
                threads[-1].start()

                newReadPtr = uploadedFile.tell()
                chunks.append({ "chunkNumber": chunkCtr, "name": chunkmd5, "size": newReadPtr - prevReadPtr })
                totalFileSize += newReadPtr - prevReadPtr
                chunkCtr += 1
                prevReadPtr = newReadPtr

            for t in threads:
                t.join()

            end = time.time()
            uploadtime = end - start
            app.logger.info("Upload successfully in secs %s",str(uploadtime))

            # save file-chunk mapping in registry
            _saveFilemapInRegistry(uploadedFile.filename, chunks)
            uploadedFile.close()
            
            # uploadedFile.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploadedFile.filename)))
            return make_response(jsonify(
                {
                    "msg":"file uploaded successfully",
                    "uploaded": True,
                    "uploadtime": uploadtime,
                    "filesize": totalFileSize,
                    "md5": runningMD5.hexdigest(),
                    "chunks": chunks
                }
                ),200
                )
        except Exception as e:
            return make_response(jsonify({"msg":str(e)}),500)
   
@app.route("/download", methods = ['GET'])
def download():
    app.logger.info("in download")
    try:
        filename = request.args.get('filename')
        if not "." in filename:
            app.logger.info("download %s",filename)
            return make_response(jsonify({"msg":"invalid file name"}),400)

        ext = filename.rsplit(".", 1)[1]
        if ext.upper() not in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
            return make_response(jsonify({"msg":"invalid file extension"}),400)
        
        # get file-chunk mapping from registry
        # sample chunks = [
        #     {
        #         "chunkNumber": 1,
        #         "name": "348f95c89947ac4be76faabdcf660e65",
        #         "size": 31457280,
        #         "url": "127.0.0.1:2750"
        #     },
        #     {
        #         "chunkNumber": 2,
        #         "name": "907e39b684bda5bfd0308f281628664c",
        #         "size": 20257792,
        #         "url": "127.0.0.1:2750"
        #     }
        # ]
        chunks = _getFilemapFromRegistry(filename)

        start = time.time()
        _createDownloadFolder()
        threads = []
        for obj in chunks:
            threads.append(threading.Thread(target=__downloadChunk, args=(obj,),))
            threads[-1].start()

        for t in threads:
            t.join()

        # ok to stop timer here since all chunks have been downloaded parallelly
        end = time.time()

        # all chunks are now downloaded, calculate time taken to download chunks
        downloadtime = end - start
        app.logger.info("Downloaded successfully in secs %s",str(downloadtime))

        # merge all chunks, delete individual chunk files after appending
        __mergeChunkFiles(filename, chunks)

        # return send_file('/Users/abhijeetlimaye/Desktop/test.txt', attachment_filename='python.txt')
        return make_response(jsonify(
            {
                "msg":"file downloaded successfully",
                "downloadtime":downloadtime
            }
            ),200
            )
    except Exception as e:
        return make_response(jsonify({"msg":str(e)}),500)

#get list of files in service registry
@app.route("/getfilelist", methods=['GET'])
def getfilelist():
    try:
        raw_response = requests.get(SERVICE_REGISTRY_URL + "/getfilelist")
        obj = raw_response.json()
        return make_response(obj, 200)
    except Exception as e:
         return make_response(jsonify({"msg":str(e)}),500)

#get list of servers in service registry
@app.route("/getserverlist", methods=['GET'])
def getserverlist():
    try:
        raw_response = requests.get(SERVICE_REGISTRY_URL + "/getserverlist")
        obj = raw_response.json()
        return make_response(obj, 200)
    except Exception as e:
        return make_response(jsonify({"msg":str(e)}),500)



def __mergeChunkFiles(mergedFilename, chunks):
    mergedFile = open(os.path.join(DOWNLOAD_FOLDER, mergedFilename), "wb")
    for dict in chunks:
        chunkHandle = open(os.path.join(DOWNLOAD_FOLDER, dict['name']), "rb")
        while True:
            chunk = chunkHandle.read(MAX_FILE_SIZE)
            if not chunk:
                chunkHandle.close()
                os.remove(os.path.join(DOWNLOAD_FOLDER, dict['name']))
                break
            mergedFile.write(chunk)
    mergedFile.close()

def __downloadChunk(obj):
    chunkName = obj['name']
    fileHandle = open(os.path.join(DOWNLOAD_FOLDER, chunkName), "wb")
    grpcServerIP = obj['url']
    app.logger.info("Starting download for %s from %s", chunkName, grpcServerIP)
    fileserver_client.Client().download(chunkName, grpcServerIP, fileHandle)
    app.logger.info("Downloaded chunk %s successfully from %s", chunkName, grpcServerIP)
    fileHandle.close()

def __uploadChunk(chunk, chunkName):
    grpcServerIP = __getStreamingServerAddress(chunkName)
    app.logger.info("Starting upload for %s at %s", chunkName, grpcServerIP)
    fileserver_client.Client().upload(BytesIO(chunk), grpcServerIP, chunkName)
    app.logger.info("Uploaded chunk %s successfully at %s", chunkName, grpcServerIP)

def _saveFilemapInRegistry(filename, fileMap):
    data = { "filename": filename, "chunks": json.dumps(fileMap)}
    try:
        raw_response = requests.post(SERVICE_REGISTRY_URL + "/savefilemap", data = data)
        obj = raw_response.json()
        return obj[filename]
    except Exception as e:
        app.logger.warning("%s",str(e))

def _getFilemapFromRegistry(filename):
    params = { 'filename': filename }
    try:
        raw_response = requests.get(SERVICE_REGISTRY_URL + "/getfilemap", params = params)
        obj = json.loads(raw_response.text)
        return obj[filename]
    except Exception as e:
        app.logger.warning("%s",str(e))

def __getStreamingServerAddress(md5):
    filemd5 = {'md5': md5}
    try:
        raw_response = requests.get(SERVICE_REGISTRY_URL + "/getserver", params = filemd5)
        obj = raw_response.json()
        app.logger.warning(obj)
        return obj['msg']
    except Exception as e:
        app.logger.warning("%s",str(e))

def _createDownloadFolder():
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
        app.logger.info("created /downloads folder")
    else:
        app.logger.info("/downloads folder exists")
    app.logger.info(DOWNLOAD_FOLDER)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
