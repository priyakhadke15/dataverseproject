from flask import Flask,request,jsonify, make_response
from werkzeug.utils import secure_filename
import logging,os

app = Flask(__name__)
file_handler = logging.FileHandler('server.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))

@app.route("/")
def index():
    return "Test Route!"

@app.route("/upload", methods = ['POST'])
def upload():
    if request.method == 'POST' and request.files['file']:
        try:
            _createFolder()
            uploadedFile = request.files['file']
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