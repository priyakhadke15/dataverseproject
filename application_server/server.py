from flask import Flask,request,jsonify, make_response,send_file
from werkzeug.utils import secure_filename
import logging,os
import sys
import time
import hashlib
import requests

sys.path.append('../')
import fileserver_client

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = '{}/uploads/'.format(PROJECT_HOME)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF","TXT","DOC","DOCX","PDF","MKV","AVI","DIVX","MP4"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024
serviceRegistry_url = 'http://0.0.0.0:5001/getserver'

@app.route("/")
def index():
    return "Test Route!"

@app.route("/upload", methods = ['POST'])
def upload():
    if request.files['file']:
        try:
            uploadedFile = request.files['file']
            if not "." in uploadedFile.filename:
                print(uploadedFile.filename)
                return make_response(jsonify({"msg":"invalid file name"}),400)

            ext = uploadedFile.filename.rsplit(".", 1)[1]
            if ext.upper() not in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                 return make_response(jsonify({"msg":"invalid file extension"}),400)
           
            file_size = len(uploadedFile.read())
            uploadedFile.seek(0)
            md5 = hashlib.md5(uploadedFile.read()).hexdigest()
            uploadedFile.seek(0)
            # if int(file_size) > app.config["MAX_IMAGE_FILESIZE"]:
            #     return False

            grpcServerIP = __getServerAddress(md5)
            app.logger.info("Starting upload at %s",grpcServerIP)

            start = time.time()
            success = fileserver_client.Client().upload(uploadedFile,grpcServerIP)
            end = time.time()
            if not success:
                app.logger.info("upload failed")
                return make_response(jsonify({"msg":"File not uploaded"}),500)
            uploadtime = end - start
            app.logger.info("Upload successfully in secs %s",str(uploadtime))
            
            # uploadedFile.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploadedFile.filename)))
            return make_response(jsonify(
                {
                    "msg":"file uploaded successfully",
                    "uploaded": success,
                    "uploadtime": uploadtime,
                    "filesize": file_size,
                    "md5": md5
                }
                ),200
                )
        except Exception,e:
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
        
        grpcServerIP = __getServerAddress(filename)
        app.logger.info("Starting download from %s", grpcServerIP)
        start = time.time()
        success = fileserver_client.Client().download(filename, grpcServerIP)
        end = time.time()

        if not success:
            app.logger.info("download failed")
            return make_response(jsonify({"msg":"File not downloaded"}),500)
        downloadtime = end - start
        app.logger.info("Downloaded successfully in secs %s",str(downloadtime))
        # return send_file('/Users/abhijeetlimaye/Desktop/test.txt', attachment_filename='python.txt')
        return make_response(jsonify(
            {
                "msg":"file downloaded successfully",
                "downloadtime":downloadtime
            }
            ),200
            )
    except Exception,e:
        return make_response(jsonify({"msg":str(e)}),500)

def __getServerAddress(md5):
    filemd5 = {'md5': md5}
    try:
        raw_response = requests.get(serviceRegistry_url, params = filemd5)
        app.logger.info("%s",raw_response)
        obj = raw_response.json()
        return obj['msg']
    except Exception as e:
        app.logger.warning("%s",str(e))

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
