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

btsrp_url = 'http://192.168.1.2:5000' # communication details for bootstrap node
# btsrp_url = 'http://192.168.2.10:5000'
myNode = node.Node()

#.......................................................................................
# REST services and functions
#.......................................................................................


# bootstrap node initializes the app
# create genesis block and add boostrap to dict to be broadcasted
# OK
@app.route('/init/<total_nodes>', methods=['GET'])
def init_connection(total_nodes):
	global TOTAL_NODES
	TOTAL_NODES = int(total_nodes)
	print('App starting for ' + str(TOTAL_NODES) + ' nodes')
	genesis_trans = myNode.create_genesis_transaction(TOTAL_NODES)
	myNode.valid_chain.create_blockchain(genesis_trans) # also creates genesis block
	myNode.id = 0
	myNode.register_node_to_ring(myNode.id, str(request.environ['REMOTE_ADDR']), '5000', myNode.wallet.public_key)	##TODO: add the balance
	print('Bootstrap node created: ID = ' + str(myNode.id) + ', blockchain with ' + str(len(myNode.valid_chain.block_list)) + ' block')

	return render_template('app_start.html')


# node requests to boostrap connect to the ring
# OK
@app.route('/connect', methods=['GET'])
def connect_node_request():
	print('Node wants to connect')
	myIP = str(request.environ['REMOTE_ADDR'])
	# myPort = str(request.environ['REMOTE_PORT'])
	myInfo = 'http://' + myIP + ':5000'
	message = {'ip':myIP, 'port':'5000', 'public_key':myNode.wallet.public_key}
	message['flag']=0 # flag=0 if connection request
	m = json.dumps(message)
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	response = requests.post(btsrp_url + "/receive", data = m, headers = headers)
	
	data = response.json() # dictionary containing id + chain
	potentialID = data.get('id')
	current_chain = data.get('chain')
	current_utxos = data.get('utxos')
	
	if potentialID > 0:
		print("____CONNECTED____")
		myNode.id = potentialID
		myNode.wallet.utxos = current_utxos
		message={}
		message['public_key']=myNode.wallet.public_key
		message['flag']=1 # if request success and transaction is due
		response = requests.post(btsrp_url + "/receive", data = json.dumps(message), headers = headers)
		return "Connection for IP: " + myIP + " established,\nOK\n",200
	else:
		return "Conection for IP: " + myIP + " to ring refused, too many nodes\n",403
	

# bootstrap handles node requests to join the ring
# OK
@app.route('/receive', methods=['POST'])
def receive_node_request():
	global NODE_COUNTER
	global TOTAL_NODES
	receivedMsg = request.get_json()
	if (receivedMsg.get('flag')==0):
		senderInfo = 'http://' + str(request.environ['REMOTE_ADDR']) + ':' + receivedMsg.get('port')
		print(senderInfo)
		newID = -1
		print("total:%d, counter:%d\n"%(TOTAL_NODES,NODE_COUNTER))
		
		if  NODE_COUNTER < TOTAL_NODES - 1:
			NODE_COUNTER += 1
			newID = NODE_COUNTER
			myNode.register_node_to_ring(newID, str(request.environ['REMOTE_ADDR']), receivedMsg.get('port'), receivedMsg.get('public_key'))	##TODO: add the balance
			new_data = {}
			new_data['id'] = newID
			new_data['utxos'] = myNode.wallet.utxos
			blocks = []
			for block in myNode.valid_chain.block_list:
				tmp=block.__dict__
				tmp['listOfTransactions']=block.listToSerialisable()
				blocks.append(tmp)
			new_data['chain'] = blocks
			message = json.dumps(new_data)
			print("__BOOT_WALLET__")
			print(myNode.wallet.utxos)
			return message, 200 # OK
		else:
			print(myNode.ring)
			return "Too many nodes already\n",403 #FORBIDDEN
	
	if (receivedMsg.get('flag')==1):
		myNode.create_transaction(myNode.wallet,receivedMsg.get('public_key'),100) # give 100 NBCs to each node
		return "Transfered 100 NBCs to Node", 200 # OK


# receive broadcasted transaction
# CHECK with validate functionality
@app.route('/receive_trans',methods=['POST'])
def receive_trans():
	print("node received a transaction")
	data = request.get_json()
	trans = transaction.Transaction(**data)
	code, t = myNode.validate_transaction(trans) # added or error
	if (code =='added'):
		print("Node %s: -Transaction from %s to %s is valid\n"%(myNode.id,data.get('sender'),data.get('receiver')))
		isBlockMined = myNode.add_transaction_to_block(trans)
		if (isBlockMined):
			return "Valid transaction added to block, block is mined OK\n",200
		else:
			return "Valid transaction added to block OK\n",200
	else:
		return "Error: Illegal Transaction\n",403


# receive broadcasted block
# CHECK with validate functionality
@app.route('/receive_block', methods = ['POST'])
def receive_block():
	data = request.get_json()
	b = block.Block()
	b.previousHash = data.get('previousHash')
	b.timestamp = data.get('timestamp')
	b.nonce = data.get('nonce')
	b.listOfTransactions = data.get('listOfTransactions')
	b.blockHash = data.get('hash')
	if (b.nonce != 1 and myNode.validate_block(b)):
		print("Node %s: -Block validated\n"%myNode.id)
	else:
		return "Error: Block rejected\n", 403
	return "Block broadcast OK\n",200


# create new transaction
# FILLME
@app.route('/transaction/new',methods=['POST'])
def transaction_new():
	data = request.get_json()
	amount=data.get('amount')
	recipient_address=data.get('recipient_address')
	wallet=myNode.wallet()
	myNode.create_transaction(wallet,recipient_address,amount)
	return


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