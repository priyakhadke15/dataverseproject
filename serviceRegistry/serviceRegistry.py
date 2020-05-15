from flask import Flask,request,jsonify, make_response,send_file
import logging,os
import time

app = Flask(__name__)
file_handler = logging.FileHandler('serviceRegistry.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
serverMap = dict()

@app.route("/")
def index():
    return "Test Route!"

# API to get the server from available GRPC servers
@app.route("/getserver", methods=['GET'])
def getserver():
    return "get server"

# API to register the server once GRPC server is initiated
@app.route("/register", methods=['POST'])
def register():
    try:
        ipaddress = request.values.get('ipaddress')
        portno = request.values.get('port')
        serverMap[ipaddress+":"+portno] = round(time.time())
        return serverMap
    except Exception as e:
        return make_response(jsonify({"msg":str(e)}),500)

# API to send the GRPC server heartbeat to service registery
@app.route("/heartbeat", methods=['PUT'])
def heartbeat():
    try:
        ipaddress = request.values.get('ipaddress')
        portno = request.values.get('port')
        key = ipaddress+":"+portno
        if key not in dict.keys(serverMap): 
            logging.info("not registered service")
            return make_response(jsonify({"msg":"GRPC server not registered"}),400)
        serverMap[key] = round(time.time())
        return serverMap
    except Exception as e:
        return make_response(jsonify({"msg":str(e)}),500)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5001,debug=True)