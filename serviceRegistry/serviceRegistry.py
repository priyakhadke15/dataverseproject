from flask import Flask,request,jsonify, make_response,send_file
import logging,os
import time
from uhashring import HashRing 

# init vars
app = Flask(__name__)
file_handler = logging.FileHandler('serviceRegistry.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
serverMap = dict()
# create a consistent hash ring of 3 nodes of weight 1
hr = HashRing(nodes=[])
INACTIVE_SERVER_TIMEOUT = 30 #5 secs

@app.route("/")
def index():
    return "Test Route!"

# API to get the server from available GRPC servers using the md5 value
@app.route("/getserver", methods=['GET'])
def getserver():
    try:
        # remove the inactive servers from dictionary
        delete = [key for key in serverMap if time.time()-serverMap[key] > INACTIVE_SERVER_TIMEOUT] 
        print("Marked for del",delete)
        
        for key in delete: 
            print("Remove the inactive server ",key)  
            del serverMap[key]
            hr.remove_node(key)
       
        md5 = request.args.get('md5')
        # get the node name for the md5 key
        target_node = hr.get_node(md5)
        return make_response(jsonify({"msg":target_node}),200)
    except Exception as e:
        return make_response(jsonify({"msg":str(e)}),500)
    

# API to register the server once GRPC server is initiated
@app.route("/register", methods=['POST'])
def register():
    try:
        ipaddress = request.values.get('ipaddress')
        portno = request.values.get('port')
        key = ipaddress+":"+portno
        serverMap[key] = round(time.time())
        # add back node2
        hr.add_node(key)
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