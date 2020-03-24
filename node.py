import block
import blockchain
import wallet
import json
import requests
import transaction
import copy
from Crypto.Hash import SHA256

MINING_DIFFICULTY = 5
CAPACITY = 5 # run capacity=1, 5, 10
init_count = -1 #initial id count, accept ids <= 10

class Node:
	def __init__(self,NUM_OF_NODES=None):
		print('node_init')
		self.wallet = wallet.Wallet()
		self.id = -1 # bootstrap will send the node's final ID
		self.valid_chain = blockchain.Blockchain()
		self.current_block = None # where received transactions are collected
		self.ring = {} #here we store information for every node, as its id, its address (ip:port) its public key and its balance


	def broadcast(message, url):
		m = json.dump(message)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		for nodeID in self.ring:
			nodeInfo = self.ring[nodeInfo]
			requests.post(nodeInfo[ip]+"/"+url, data = m, headers = headers)
		return


	#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
	def register_node_to_ring(self, nodeID, ip, port, public_key):
		if self.id == 0:
			print(self.id)
			self.ring[nodeID] = {'ip': ip,'port': port,'public_key': public_key}
			print('register_node')
		else:
			print('cannot register node')


	def create_genesis_transaction(self,num_of_nodes):
		data={}
		sender=self.wallet.public_key
		amount=100*num_of_nodes

		# create genesis transaction
		data['receiver']=data['sender']=sender
		data['transaction_inputs']=[]
		data['transaction_outputs']=[]
		outpt_sender = outpt_receiver = {"id":0,"to_who":sender,"amount":amount}
		data['transaction_outputs'].append(outpt_sender)
		data['transaction_outputs'].append(outpt_receiver)
		data['id']=0
		data['signature']=None
		data['sender_privkey']=self.wallet.private_key
		data['amount']=amount
		trans = transaction.Transaction(**data)
		# add transaction to block
		self.valid_chain.block_list[-1].listOfTransactions.append(trans)

		# add genesis UTXO to wallet
		init_utxos={}
		init_utxos[sender]={"id":0,"to_who":sender,"amount":amount}
		self.wallet.utxos=init_utxos
		

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
				inputs.append(utxo['id'])
				if (sum>=amount):
					break
			trxn= Transaction(key, sender_wallet.private_key, receiver_public, amount, inputs)
			trxn.sign_transaction() #set id & signature
			if(sum>amount):
				trxn.transaction_outputs.append({'id': trxn.id, 'to_who': trxn.sender, 'amount': sum-trxn.amount})
			trxn.transaction_outputs.append({'id': trxn.id, 'to_who':trxn.receiver, 'amount': trxn.amount})
			return trxn

		except Exception as e:
			print(f"create_transaction: {e.__class__.__name__}: {e}")
			return None
		

	def broadcast_transaction(self,trans):
		print("broadcast_transaction")
		url = "receive_trans"
		message = trans.__dict__ #returns attributes as keys, and their values as value
		broadcast(message,url)
		return


	def validate_transaction(self, t):
		#use of signature and NBCs balance
		print("validate_transaction")
		try:
			# verify signature
			if not t.verify_signature():
				raise Exception('invalid signature')
			if t.sender == t.receiver:
				raise Exception('sender must be different from recepient')
			if t.amount <= 0:
				raise Exception('negative amount?')
			sender_utxos= copy.deepcopy(self.wallet.utxos[t.sender])
			val_amount=0
			for t_id in t.transaction_inputs:
				found=False
				for utxo in sender_utxos:
					if utxo['id']== t_id and utxo['to_who']==t.sender:
						found=True
						val_amount += utxo['amount']
						sender_utxos.remove(utxo)
						break
				if not found:
					raise Exception('missing transaction inputs')
			temp = []
			if (val_amount >= t.amount):
				temp.append({'id': t.id, 'to_who': t.sender, 'amount': val_amount - t.amount })
				temp.append({'id': t.id, 'to_who': t.sender, 'amount':  t.amount })
			if (temp != t.transaction_outputs):
				raise Exception('Wrong outputs')

			if(len (t.transaction_outputs) == 2):
				sender_utxos.append(t.transaction_outputs[0]) #removed old utxos , added
				self.wallet.utxos[t.sender]=sender_utxos
				self.wallet.utxos[t.receiver].append(t.transaction_outputs[1])
			else:
				self.wallet.utxos[t.sender]=sender_utxos
				self.wallet.utxos[t.receiver].append(t.transaction_outputs[0])

			return 'added',t

		except Exception as e:
			print(f"validate transaction: {e.__class__.__name__}: {e}")
			return 'error', None


	# add transaction to block and mine if it is full
	# return True if it is mined, else False
	def add_transaction_to_block(self,transaction):
		global CAPACITY
		print("add_transaction_to_block")
		self.current_block.listOfTransactions.append(transaction)
		if len(self.current_block.listOfTransactions) == CAPACITY:
			mine_block(self.current_block)
			return True
		else:
			return False


	def mining_hash(self, block):
		tmp = f"{block.index}{block.previousHash}{block.timestamp}{block.nonce}{block.listOfTransactions}"
		tmpEncode = tmp.encode()
		return SHA256.new(tmpEncode).hexdigest() 


	# mine when current block is full
	# the one who finds the right nonce broadcast the block
	def mine_block(self, block, difficulty = MINING_DIFFICULTY):
		print("mine_block")
		self.nonce = 0
		guess = mining_hash(block)
		while guess[:difficulty]!=('0'*difficulty):
			self.nonce += 1
			guess = mining_hash(block)
		block.hash = guess
		broadcast_block(block)


    # add block to node's valid chain
    # and return a new current one
	def create_new_block(self, block):	 ##TODO: check if we should do it also for genesis
		print("create_block")
		self.valid_chain.add_block(block)
		idx = block.index + 1
		prevHash = block.hash
		self.current_block = block.Block(index = idx, previousHash = prevHash)


	# broadcast current block, added to chain and initialize new one
	def broadcast_block(self, block):
		print("broadcast_block")
		url = "receive_block"
		message = block.__dict__
		broadcast(message, url)
		create_new_block(block)
		return

	
	def validate_block(self, block):
		print("validate_block\n")
		return block.previousHash == self.valid_chain.block_list[-1].hash


	def valid_proof(nonce, difficulty=MINING_DIFFICULTY):
		print("valid_proof")
		return nonce[:difficulty] == '0'*difficulty

	def validate_chain(self):
		for b in self.valid_chain.block_list:
			if ( not self.validate_block(b)):
				return False
		return True

	#consensus functions
	def valid_chain(self, chain):
		#check for the longer chain across all nodes
		print("valid_chain")

	def resolve_conflicts(self):
		#resolve correct chain
		print("resolve_conflicts")


