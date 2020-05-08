from flask import Flask,request
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
    if request.method == 'POST':
        _createFolder()
    return "Hello World!"

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