import block
import wallet
import json
import requests
import transaction

MINING_DIFFICULTY = 5
CAPACITY = 5 # run capacity=1, 5, 10
init_count = -1 #initial id count, accept ids <= 10

class Node:
	def __init__(self,NUM_OF_NODES=None):
		print('node_init')
		self.NBC=100;
		self.wallet=wallet.Wallet()
		self.id=-1 # bootstrap will send the node's final ID
		self.valid_chain=None
		self.ring={} #here we store information for every node, as its id, its address (ip:port) its public key and its balance 


	def broadcast(message,url):
		m = json.dump(message)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		for other in self.ring:
			requests.post(other+"/"+url, data = m, headers = headers)
		return

	def create_new_block():
		print("create_block")
	
	# def create_wallet():
	# 	#create a wallet for this node, with a public key and a private key
		# print("create_wallet")
		
	
	#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
	def register_node_to_ring(self, nodeID, ip, port, public_key):
		if self.id == 0:
			print(self.id)
			self.ring[nodeID] = {'ip': ip,'port': port,'public_key': public_key}
			print('register_node')
		else:
			print('cannot register node')


	def create_transaction(sender_wallet, receiver_public, amount):
		#remember to broadcast it
		print("create_transaction")
		sum = 0
		inputs = []
		try:
			if(sender_wallet.balance() < amount):
				raise Exception("not enough money")

			key=sender_wallet.public_key
			for utxo in sender_wallet.utxos[key]:
				sum=sum+utxo['amount']
				inputs.append(utxo)
				if (sum>=amount):
					break
			trxn= Transaction(key, sender_wallet.private_key, receiver_public, amount, inputs)
			trxn.sign_transaction()
			if(sum>amount):
				trxn.transaction_outputs.append({'id': trxn.id, 'to_who': trxn.sender, 'amount': sum-trxn.amount})
			trxn.transaction_outputs.append({'id': trxn.id, 'to_who':trxn.receiver, 'amount': trxn.amount})
			return trxn

		except Exception as e:
			print(f"create_transaction: {e.__class__.__name__}: {e}")
			return None
		

	def broadcast_transaction():
		print("broadcast_transaction")


	def validate_transaction():
		#use of signature and NBCs balance
		print("validate_transaction")


	def add_transaction_to_block():
		#if enough transactions  mine
		print("add_transaction_to_block")


	def mine_block():
		print("mine_block")


	def broadcast_block():
		print("broadcast_block")

		

	def valid_proof(other_parameters, difficulty=MINING_DIFFICULTY):
		print("valid_proof")



	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes
		print("valid_chain")

	def resolve_conflicts(self):
		#resolve correct chain
		print("resolve_conflicts")


