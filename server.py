from flask import Flask,request,jsonify, make_response
from werkzeug.utils import secure_filename
import logging,os

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF","TXT","DOC","DOCX","PDF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

@app.route("/")
def index():
    return "Test Route!"

@app.route("/upload", methods = ['POST'])
def upload():
    if request.method == 'POST' and request.files['file']:
        try:
            uploadedFile = request.files['file']
            if not "." in uploadedFile.filename:
                return make_response(jsonify({"msg":"invalid file name"}),400)

            ext = uploadedFile.filename.rsplit(".", 1)[1]
            if ext.upper() not in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
                 return make_response(jsonify({"msg":"invalid file extension"}),400)
           
            # file_size = os.stat('/Users/abhijeetlimaye/Desktop/test.txt').st_size
            # if int(file_size) > app.config["MAX_IMAGE_FILESIZE"]:
            #     return False

            _createFolder()
            app.logger.info(uploadedFile.stream._max_size)
            uploadedFile.save(secure_filename(uploadedFile.filename))
            return make_response(jsonify(
                {
                    "msg":"file uploaded successfully"
                }
                ),200
                )
        except:
            return make_response(jsonify({"msg":"File not uploaded"}),500)
   

def _createFolder():
    _UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)

    if not os.path.exists(_UPLOAD_FOLDER):
        os.makedirs(_UPLOAD_FOLDER)
        app.logger.info("created uploads folder")
    else:
        app.logger.info("uploads folder exists")

    app.config['UPLOAD_FOLDER'] = _UPLOAD_FOLDER
    app.logger.info(app.config['UPLOAD_FOLDER'])

if __name__ == "__main__":
    app.run(debug=True)