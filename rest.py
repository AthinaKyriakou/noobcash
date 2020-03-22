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

TOTAL_NODES = 0
NODE_COUNTER = 0 
BROAD_BUDDIES = {}	# dictionary of (ip address:port,public key) per node id

btsrp_url = "http://83.212.72.137:5000" # communication details for bootstrap node

myNode = node.Node()
myChain = blockchain.Blockchain()

#.......................................................................................
# REST services and functions
#.......................................................................................


# bootstrap node initializes the app

@app.route('/init/<total_nodes>', methods=['GET'])
def init_connection(total_nodes):
	global TOTAL_NODES
	global BROAD_BUDDIES
	TOTAL_NODES = int(total_nodes)
	
	# create genesis block and add boostrap to dict to be broadcasted
	print('App starting for ' + str(TOTAL_NODES) + ' nodes')
	myChain.create_blockchain()
	myNode.id = 0
	BROAD_BUDDIES[myNode.id] = {'ip':str(request.environ['REMOTE_ADDR']),'port':'5000','public_key':myNode.wallet.public_key}

	print('Bootstrap node created: ID = ' + str(myNode.id) + ', blockchain with ' + str(len(myChain.block_list)) + ' block')
	return render_template('app_start.html')


# node requests to boostrap connect to the ring

@app.route('/connect', methods=['GET'])
def connect_request():
	
	## TODO
	print('Node wants to connect')
	myIP = str(request.environ['REMOTE_ADDR'])
	# myPort = str(request.environ['REMOTE_PORT'])
	myInfo = 'http://' + myIP + ':5000'

	message = {'ip':myIP, 'port':'5000', 'public_key':myNode.wallet.public_key}
	m = json.dumps(message)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	response = requests.post(btsrp_url + "/receive", data = m, headers = headers)

	## TODO: set ID to node if accepted in the ring
	print(response)
	
	return myIP + ' tries to get iiiiiiin'


# bootstrap handles node requests to join the ring

@app.route('/receive', methods=['POST'])
def receive_node_req():
	global NODE_COUNTER
	global TOTAL_NODES
	global BROAD_BUDDIES
	message = request.get_json()
	if  NODE_COUNTER < TOTAL_NODES - 1:
		NODE_COUNTER += 1
		BROAD_BUDDIES[NODE_COUNTER] = {'ip': message.get('ip'), 'port': message.get('port'), 'public_key': message.get('public_key')}
		print('Node ' + str(NODE_COUNTER) + ' added')
		return 'ok', 200
	else:
		print('Too many nodes already ' + str(NODE_COUNTER))
		print(BROAD_BUDDIES)
		return 'prob', 400
	
	
# get all transactions in the blockchain

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
    transactions = blockchain.transactions
    response = {'transactions': transactions}
    return jsonify(response), 200


# run it once for every node

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)