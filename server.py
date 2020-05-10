from flask import Flask,request,jsonify, make_response
from werkzeug.utils import secure_filename
import logging,os
import fileserver_client
import time

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = '{}/uploads/'.format(PROJECT_HOME)
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF","TXT","DOC","DOCX","PDF","MKV","AVI","DIVX","MP4"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

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
           
            # file_size = len(uploadedFile.read())
            # if int(file_size) > app.config["MAX_IMAGE_FILESIZE"]:
            #     return False

            _createFolder()
            app.logger.info("Starting upload")
            start = time.time()
            success = fileserver_client.Client().upload(uploadedFile)
            end = time.time()
            if not success:
                app.logger.info("upload failed")
                return make_response(jsonify({"msg":"File not uploaded"}),500)
            uploadtime = end - start
            app.logger.info("Upload time in secs %s",str(uploadtime))
            
            # uploadedFile.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(uploadedFile.filename)))
            return make_response(jsonify(
                {
                    "msg":"file uploaded successfully",
                    "uploaded": success,
                    "uploadtime":uploadtime
                }
                ),200
                )
        except Exception,e:
            return make_response(jsonify({"msg":str(e)}),500)
   

def _createFolder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        app.logger.info("created uploads folder")
    else:
        app.logger.info("uploads folder exists")
    app.logger.info(app.config['UPLOAD_FOLDER'])

if __name__ == "__main__":
    app.run(debug=True)