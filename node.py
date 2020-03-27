import block
import blockchain
import wallet
import json
import requests
import transaction
import copy
from Crypto.Hash import SHA256

MINING_DIFFICULTY = 2
CAPACITY = 5 # run capacity=1, 5, 10
init_count = -1 #initial id count, accept ids <= 10

class Node:
	def __init__(self,NUM_OF_NODES=None):
		print('node_init')
		self.wallet = wallet.Wallet()
		self.id = -1 # bootstrap will send the node's final ID
		self.valid_chain = blockchain.Blockchain()
		self.current_block = block.Block() # where received transactions are collected
		self.ring = {} #here we store information for every node, as its id, its address (ip:port) its public key and its balance


	def toURL(self,nodeID):
		url = "http://%s:%s"%(self.ring[nodeID]['ip'],self.ring[nodeID]['port'])
		return url

	def broadcast(self,message, url):
		m = json.dumps(message)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		for nodeID in self.ring:
			if(nodeID == self.id): # don't broadcast to myself
				continue
			nodeInfo = self.toURL(nodeID)
			requests.post(nodeInfo+"/"+url, data = m, headers = headers)
		return

	def broadcast_transaction(self,trans):
		print("broadcast_transaction")
		url = "receive_trans"
		message = trans.__dict__ #returns attributes as keys, and their values as value
		self.broadcast(message,url)
		return

	# broadcast current block
	# initialize new one for receiving transactions
	def broadcast_block(self, block):
		print("broadcast_block")
		url = "receive_block"
		message = block.__dict__
		message['listOfTransactions'] = block.listToSerialisable()
		self.broadcast(message, url)
		create_new_block(block)
		return


	#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
	#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
	def register_node_to_ring(self, nodeID, ip, port, public_key):
		if self.id == 0:
			self.ring[nodeID] = {'ip': ip,'port': port,'public_key': public_key}
			if(self.id!=nodeID):
				self.wallet.utxos[public_key]=[] # initialize utxos of other nodes
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
		trans = transaction.Transaction(**data) # genesis transaction

		# add genesis UTXO to wallet
		init_utxos={}
		init_utxos[sender]=[{"id":0,"to_who":sender,"amount":amount}]
		self.wallet.utxos=init_utxos # bootstrap wallet with 100*n NBCs
		return trans

	def create_transaction(self,sender_wallet, receiver_public, amount):
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
			trxn= copy.deepcopy(transaction.Transaction(key, sender_wallet.private_key, receiver_public, amount, inputs))
			trxn.sign_transaction() #set id & signature
			if(sum>amount):
				trxn.transaction_outputs.append({'id': trxn.id, 'to_who': trxn.sender, 'amount': sum-trxn.amount})
			trxn.transaction_outputs.append({'id': trxn.id, 'to_who':trxn.receiver, 'amount': trxn.amount})
			self.broadcast_transaction(trxn)
			self.validate_transaction(trxn) # Node validates the trxn it created
			return trxn

		except Exception as e:
			print(f"create_transaction: {e.__class__.__name__}: {e}")
			return None


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
				temp.append({'id': t.id, 'to_who': t.receiver, 'amount':  t.amount })

			if (temp != t.transaction_outputs):
				raise Exception('Wrong outputs')

			if(t.receiver not in self.wallet.utxos.keys()): # no transaction has been made with receiver, initialize his wallet
				self.wallet.utxos[t.receiver]=[]
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


	# mine when current block is full
	# the one who finds the right nonce broadcast the block
	def mine_block(self, block, difficulty = MINING_DIFFICULTY):
		print("mine_block")
		block.nonce = 0
		guess = block.myHash()
		while guess[:difficulty]!=('0'*difficulty):
			block.nonce += 1
			guess = block.myHash()
		block.hash = guess
		print("Mining succeded!\n")
		self.broadcast_block(block)


    # initialize a new current_block
    ##TODO: check if we should do it also for genesis
	def create_new_block(self, block):	 
		print("create_block")
		idx = block.index + 1
		prevHash = block.hash
		self.current_block = block.Block(index = idx, previousHash = prevHash)


	def validate_block(self, block):
		print("validate_block\n")
		return block.previousHash == self.valid_chain.block_list[-1].hash


	# def valid_proof(nonce, difficulty=MINING_DIFFICULTY):
	# 	print("valid_proof")
	# 	return nonce[:difficulty] == '0'*difficulty

	def validate_my_chain(self):
		for b in self.valid_chain.block_list:
			if (not self.validate_block(b)):
				return False
		return True

	def validate_chain(self, blockchain):
		for b in blockchain:
			if (not self.validate_block(b)):
				return False
		return True

	#consensus functions
	def resolve_conflict(self):
		#resolve correct chain
		print("resolve_conflicts")
		max_length = len(self.valid_chain)
		max_id = self.id
		max_ip= self.ring[max_id]['address']
		max_port= self.ring[max_id]['port']
		#check if someone has longer block chain
		try:
			for key in self.ring:
				node=self.ring[key]
				if node['public_key'] == self.wallet.public_key:
					continue
				n_id= key
				n_ip = node['ip']
				url = f'{n_ip}/chain_length'
				response = requests.get(url)
				if response.status_code != 200:
					raise Exception('Invalid blockchain length response')

				received_blockchain_len = response.json()['length']
				if received_blockchain_len < max_length:
					print(f'consensus.{n_id}: Ignoring shorter blockchain {received_blockchain_len}')
					continue
				max_length = received_blockchain_len
				max_port = node['port']
				max_ip = n_ip
				max_id=key
			#request max blockchain & utxos with id
			url = f'{max_ip}/get_blockchain/'
			response = requests.get(url)
			if response.status_code != 200:
				raise Exception('Invalid blockchain response')
			received_blockchain = response.json()['blockchain']
			received_utxos = response.json()['utxos']
			if not self.validate_chain(received_blockchain):
					raise Exception('received invalid chain')
			self.valid_chain=received_blockchain
			self.wallet.utxos=received_utxos

		except Exception as e:
			print(f'consensus.{n_id}: {e.__class__.__name__}: {e}')


