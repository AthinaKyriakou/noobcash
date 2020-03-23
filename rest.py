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

btsrp_url = 'http://83.212.72.137:5000' # communication details for bootstrap node
myNode = node.Node()
myChain = blockchain.Blockchain()

#.......................................................................................
# REST services and functions
#.......................................................................................


# bootstrap node initializes the app
# create genesis block and add boostrap to dict to be broadcasted

@app.route('/init/<total_nodes>', methods=['GET'])
def init_connection(total_nodes):
	global TOTAL_NODES
	global BROAD_BUDDIES
	TOTAL_NODES = int(total_nodes)
	print('App starting for ' + str(TOTAL_NODES) + ' nodes')
	myChain.create_blockchain()
	myNode.id = 0
	myNode.register_node_to_ring(myNode.id, str(request.environ['REMOTE_ADDR']), '5000', myNode.wallet.public_key)	##TODO: add the balance
	print('Bootstrap node created: ID = ' + str(myNode.id) + ', blockchain with ' + str(len(myChain.block_list)) + ' block')
	return render_template('app_start.html')


# node requests to boostrap connect to the ring

@app.route('/connect', methods=['GET'])
def connect_node_request():
	print('Node wants to connect')
	myIP = str(request.environ['REMOTE_ADDR'])
	# myPort = str(request.environ['REMOTE_PORT'])
	myInfo = 'http://' + myIP + ':5000'
	message = {'ip':myIP, 'port':'5000', 'public_key':myNode.wallet.public_key}
	m = json.dumps(message)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	response = requests.post(btsrp_url + "/receive", data = m, headers = headers)
	potentialID = int(response.text)
	if potentialID > 0:
		myNode.id = potentialID
		return myIP + ' accepted in the riiiing!'
	else:
		return myIP + ' pistolii'
	

# bootstrap handles node requests to join the ring

@app.route('/receive', methods=['POST'])
def receive_node_request():
	global NODE_COUNTER
	global TOTAL_NODES
	global BROAD_BUDDIES
	receivedMsg = request.get_json()
	senderInfo = 'http://' + receivedMsg.get('ip') + ':' + receivedMsg.get('port')
	print(senderInfo)
	newID = -1
	if  NODE_COUNTER < TOTAL_NODES - 1: #TODO: check with length of the ring
		NODE_COUNTER += 1
		newID = NODE_COUNTER
		myNode.register_node_to_ring(newID, receivedMsg.get('ip'), receivedMsg.get('port'), receivedMsg.get('public_key'))	##TODO: add the balance
	else:
		print('Too many nodes already ' + str(NODE_COUNTER))
		print(myNode.ring)

	return str(newID), 200

	
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