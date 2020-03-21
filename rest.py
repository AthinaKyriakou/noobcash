import requests 
import json
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


import block
import node
import blockchain
import wallet
import transaction
import wallet


app = Flask(__name__)
CORS(app)
blockchain = blockchain.Blockchain() #here we initialize our network and create the bootstrap node
btsrp_url = "http://83.212.72.137:5000" #communication details for bootstrap node
NUM_OF_NODES = 0
myNode = node.Node()

#.......................................................................................
# REST services and functions
#.......................................................................................

# initialize the app and create blockchain

@app.route('/init/<num_of_nodes>',methods=['GET'])
def init_connection(num_of_nodes):
	print("it works!")
	NUM_OF_NODES = int(num_of_nodes)
	print(NUM_OF_NODES)
	blockchain.create_blockchain(NUM_OF_NODES) #creates bootstrap node, genesis block and blockchain
	return render_template('app_start.html')

# node request to connect to ring

@app.route('/connect_node_req',methods=['GET'])
def connect_request():
    # TODO
    print("node wants to connect")
    myIP = str(request.environ['REMOTE_ADDR'])
    # myPort = str(request.environ['REMOTE_PORT'])
    myInfo = "http://"+myIP+":5000"
    print(myInfo)
    ## TODO: check response
    message = {'ip':myIP,'port':"5000",'public_key':myNode.wallet.public_key}
    m = json.dumps(message)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    response = requests.post(btsrp_url+"/receive_node_req", data = m,headers = headers)
    return "ok!"

@app.route('/receive_node_req',methods=['POST'])
def receive_node_req():
	message = request.get_json()
	print(message)
	return "ok",300

# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions

    response = {'transactions': transactions}
    return jsonify(response), 200



# run it once fore every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)