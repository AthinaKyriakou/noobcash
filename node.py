import block
import blockchain
import wallet
import json
import requests
import transaction
import copy
from Crypto.Hash import SHA256

import os
import threading
import threadpool
import time

MINING_DIFFICULTY = 5
CAPACITY = 1		 	# run capacity = 1, 5, 10
init_count = -1 		#initial id count, accept ids <= 10


class Node:
	def __init__(self,NUM_OF_NODES=None):
		print('node_init')
		self.wallet = wallet.Wallet()
		self.id = -1 									# bootstrap will send the node's final ID
		self.valid_chain = blockchain.Blockchain()				
		self.valid_trans = []							# list of validated transactions are collected to create a new block
		self.pending_trans = []							# list of pending for approval trans
		self.ring = {} 									# store info for every node (id, address (ip:port), public key, balance)
		self.pool = threadpool.Threadpool()			# node's pool of threads (use for mining, broadcast, etc)


	def toURL(self,nodeID):
		url = "http://%s:%s"%(self.ring[nodeID]['ip'],self.ring[nodeID]['port'])
		return url


	def broadcast(self,message, url):
		m = json.dumps(message)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		print("__RING__")
		print(self.ring)
		for nodeID in self.ring:
			if(nodeID != self.id): # don't broadcast to myself
				nodeInfo = self.toURL(nodeID)
				requests.post(nodeInfo+"/"+url, data = m, headers = headers)
		return


	def broadcast_transaction(self,trans):
		print("broadcast_transaction")
		url = "receive_trans"
		message = trans.__dict__ #returns attributes as keys, and their values as value
		self.broadcast(message,url)
		return


	# converts a json list of dicts to blocks 
	# and adds them to node's block chain
	def add_block_list_to_chain(self,valid_chain_list, block_list):
		for d in block_list:
			print("add_block_list_to_chain")
			newBlock = block.Block(index = d.get('index'), previousHash = d.get('previousHash'))
			newBlock.timestamp = d.get('timestamp')
			newBlock.nonce = d.get('nonce')
			newBlock.listOfTransactions = []

			for trans_data in d.get('listOfTransactions'):
				trans = transaction.Transaction(**trans_data)
				newBlock.listOfTransactions.append(trans)

			newBlock.hash = d.get('hash')
			valid_chain_list.append(newBlock)
		return


	# broadcast current block
	# initialize new one for receiving transactions
	# TODO: fix
	def broadcast_block(self, block):
		print("broadcast_block")
		url = "receive_block"
		message = block.__dict__
		message['listOfTransactions'] = block.listToSerialisable()
		self.broadcast(message, url)
		create_new_block(block)
		return

	def broadcast_ring(self):
		url="connect/ring"
		message=self.ring
		self.broadcast(message,url)

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
				raise Exception("Not enough money!")

			key=sender_wallet.public_key
			for utxo in sender_wallet.utxos[key]:
				sum=sum+utxo['amount']
				inputs.append(utxo['id'])
				if (sum>=amount):
					break
			trxn= copy.deepcopy(transaction.Transaction(key, sender_wallet.private_key, receiver_public, amount, inputs))
			trxn.sign_transaction() #set id & signature
			if(sum>=amount):
				trxn.transaction_outputs.append({'id': trxn.id, 'to_who': trxn.sender, 'amount': sum-trxn.amount})
			trxn.transaction_outputs.append({'id': trxn.id, 'to_who':trxn.receiver, 'amount': trxn.amount})
			# print(self.validate_transaction(trxn))
			if(self.validate_transaction(self.wallet.utxos,trxn)=='validated'): # Node validates the trxn it created
				self.broadcast_transaction(trxn)
				return "Created new transaction!"
			else:
				return "Transaction not created,error"

		except Exception as e:
			print(f"create_transaction: {e.__class__.__name__}: {e}")
			return "Not enough money!"


	def validate_transaction(self,wallet_utxos, t):
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
			sender_utxos= copy.deepcopy(wallet_utxos[t.sender])
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
					#raise Exception('missing transaction inputs')
					return 'pending'
			temp = []
			if (val_amount >= t.amount):
				temp.append({'id': t.id, 'to_who': t.sender, 'amount': val_amount - t.amount })
				temp.append({'id': t.id, 'to_who': t.receiver, 'amount':  t.amount })

			if (temp != t.transaction_outputs):
				raise Exception('Wrong outputs')

			if(t.receiver not in wallet_utxos.keys()): # no transaction has been made with receiver, initialize his wallet
				wallet_utxos[t.receiver]=[]
			if(len (t.transaction_outputs) == 2):
				sender_utxos.append(t.transaction_outputs[0]) #removed old utxos , added
				wallet_utxos[t.sender]=sender_utxos	
				wallet_utxos[t.receiver].append(t.transaction_outputs[1])
			else:
				wallet_utxos[t.sender]=sender_utxos
				wallet_utxos[t.receiver].append(t.transaction_outputs[0])
			return 'validated'

		except Exception as e:
			print(f"validate transaction: {e.__class__.__name__}: {e}")
			return 'error'


	def add_transaction_to_pending(self, t):
		print("add_transaction_to_pending")
		self.pending_trans.append(t)


    # [THREAD] initialize a new_block
	def create_new_block(self, valid_trans):	 
		print("create_new_block")
		if len(self.valid_chain.block_list) == 0:
			print('Genesis block was not added properly to valid chain')
			idx = 0		# TODO: handle the bug properly
			prevHash = 0
		else:
			prevBlock = self.valid_chain.block_list[-1]
			idx = prevBlock.index + 1
			prevHash = prevBlock.hash
		newBlock = block.Block(index = idx, previousHash = prevHash)
		newBlock.listOfTransactions = valid_trans
		return newBlock


	# [THREAD]
	def mine_block(self, block, difficulty = MINING_DIFFICULTY):
		print("mine_block")
		guess = block.myHash()
		while guess[:difficulty]!=('0'*difficulty):
			block.nonce += 1
			guess = block.myHash()
		block.hash = guess
		print('Mining succeded with PoW ' + str(guess))
		print(' by{}'.format(threading.current_thread()))
		return

	# [THREAD]	
	def validate_block(self, block):
		print("validate_block")
		print('\nblock prev hash: ' + str(block.previousHash))
		print('the other: ' + str(self.valid_chain.block_list[-1].hash) + '\n')
		return block.previousHash == self.valid_chain.block_list[-1].hash and block.hash == block.myHash()


	# [THREAD] create block and call mine
	def init_mining(self, valid_trans):
		print("init_miner")
		print('Task Executed {}'.format(threading.current_thread()))
		newBlock = self.create_new_block(valid_trans)
		self.mine_block(newBlock)
		# ----- LOCK ----------
		if self.validate_block(newBlock):
			self.valid_chain.add_block(newBlock)
		# ----- UNLOCK --------
		#	self.broadcast_block(newBlock)
		return


	# add transaction to list of valid_trans
	# call mine if it is full
	# return True if mining was trigerred, else False
	def add_transaction_to_validated(self, transaction):
		global CAPACITY
		print("add_transaction_to_validated")
		self.valid_trans.append(transaction)
		if len(self.valid_trans) == CAPACITY:
			tmp = copy.deepcopy(self.valid_trans) 					# create a new block out of the valid transactions
			self.valid_trans = []									# reinitialize the valid transactions list
			future = self.pool.submit_task(self.init_mining, tmp)
			print(str(os.getpid()) + ' assigned it to mining thread')
			#TODO------- REMOVE / JUST FOR TESTING----
			#print("Main process sleeping")
			#time.sleep(60)
			#print("Main process awake")
			#print(future.done())
			#------------------------------------------
			return True				
		else:
			return False

	#Consensus functions

	def chain_REDO(self,chain):
		tmp_utxos = {}
		for b in chain[1:]:
			for trans in b.listOfTransactions:
				if(not self.validate_transasction(tmp_utxos,trans)):
					return False
		return tmp_utxos

	# validates and returns list of block objects
	def validate_chain(self, blocklist):
		chain = []
		self.add_block_list_to_chain(chain,blocklist)
		for b in chain:
			if (not self.validate_block(b)):
				return "unconfirmed list" ,False
		return chain, True

	def resolve_conflict(self):
		#resolve correct chain
		print("resolve_conflicts")
		max_length = len(self.valid_chain.block_list)
		max_id = self.id
		max_ip= self.ring[max_id]['ip']
		max_port= self.ring[max_id]['port']
		#check if someone has longer block chain
		try:
			for key in self.ring:
				node=self.ring[key]
				if node['public_key'] == self.wallet.public_key:
					continue
				n_id= key
				n_ip = node['ip']
				n_port = node['port']
				url = f'http://{n_ip}:{n_port}/chain_length'
				response = requests.get(url)
				if response.status_code != 200:
					raise Exception('Invalid blockchain length response')

				received_blockchain_len = int(response.json()['length'])
				if received_blockchain_len > max_length:
					print(f'consensus.{n_id}: Found longer blockchain => {received_blockchain_len}')
					max_length = received_blockchain_len
					max_port = n_port
					max_ip = n_ip
					max_id = n_id

			if(max_length == len(self.valid_chain.block_list)):
				return "Tie, keep existing blockchain\n"
			# request max blockchain
			url = f'http://{max_ip}:{max_port}/get_blockchain'
			response = requests.get(url)
			if response.status_code != 200:
				raise Exception('Invalid blockchain response')
			received_blocklist = response.json()['blockchain']
			new_blockchain ,valid = self.validate_chain(received_blocklist)
			if not valid:
					raise Exception('received invalid chain')
			
			# Validate all transactions in confirmed blockchain
			self.wallet.utxos=self.chain_REDO(received_blockchain)
			self.valid_chain = new_blockchain

		except Exception as e:
			print(f'consensus.{n_id}: {e.__class__.__name__}: {e}')