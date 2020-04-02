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

MINING_DIFFICULTY = 4
CAPACITY = 1		 	# run capacity = 1, 5, 10
init_count = -1 		#initial id count, accept ids <= 10

lock = threading.Lock()

class Node:
	def __init__(self,NUM_OF_NODES=None):
		print('node_init')
		self.wallet = wallet.Wallet()
		self.id = -1 									# bootstrap will send the node's final ID
		self.valid_chain = blockchain.Blockchain()			
		self.ring = {} 									# store info for every node (id, address (ip:port), public key, balance)
		self.pool = threadpool.Threadpool()				# node's pool of threads (use for mining, broadcast, etc)	
		
		self.valid_trans = []							# list of validated transactions collected to create a new block
		self.pending_trans = []							# list of pending for approval trans
		self.unreceived_trans = []						# list of transactions that are known because of a received block, they are not received individually
		self.old_valid = []								# to keep a copy of validated transactions in case miner empties them while mining

	
	def toURL(self,nodeID):
		url = "http://%s:%s"%(self.ring[nodeID]['ip'],self.ring[nodeID]['port'])
		return url

	def broadcast(self,message, url):
		print("broadcast")
		m = json.dumps(message)
		headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
		for nodeID in self.ring:
			if (nodeID != self.id):	# don't broadcast to myself
				nodeInfo = self.toURL(nodeID)
				requests.post(nodeInfo+"/"+url, data = m, headers = headers)
		return

	def broadcast_transaction(self, trans):
		url = "receive_trans"
		message = copy.deepcopy(trans.__dict__) #returns attributes as keys, and their values as value
		self.broadcast(message,url)
		return

	def broadcast_block(self, block):
		print('***node ' + str(self.id) + ' broadcast_block')
		url = "receive_block"
		message = copy.deepcopy(block.__dict__)
		message['listOfTransactions'] = block.listToSerialisable()
		#print(message)
		self.broadcast(message, url)
		return

	def broadcast_ring(self):
		#print("broadcast_ring")
		print('*** AND I WILL SEND ALL MY LOVING TO YOUUUU ***')
		print(self.ring)
		url="connect/ring"
		message=self.ring
		self.broadcast(message,url)



	# converts a json list of dicts to blocks 
	# and returns a list of block Objects
	def add_block_list_to_chain(self,valid_chain_list, block_list):
		for d in block_list:
			print("add_block_list_to_chain")
			newBlock = block.Block(index = d.get('index'), previousHash = d.get('previousHash'))
			newBlock.timestamp = d.get('timestamp')
			newBlock.nonce = d.get('nonce')
			newBlock.listOfTransactions = []		# create transactions from received dict
			for t in d.get('listOfTransactions'):
				newBlock.listOfTransactions.append(transaction.Transaction(**t))
			newBlock.hash = d.get('hash')
			valid_chain_list.append(newBlock)
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

	# get node's id in the ring, given its key
	def public_key_to_ring_id(self, public_key):
		for i in self.ring:
			d = self.ring[i]
			if d['public_key'] == public_key:
				return i



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
		data['amount']=amount
		data['senderID']=0
		data['receiverID']=0
		trans = transaction.Transaction(**data) # genesis transaction

		# add genesis UTXO to wallet
		init_utxos={}
		init_utxos[sender]=[{"id":0,"to_who":sender,"amount":amount}]
		self.wallet.utxos=init_utxos # bootstrap wallet with 100*n NBCs
		return trans

	def create_transaction(self, sender_public, senderID, receiver_public, receiverID, amount):
		print("create_transaction")
		sum = 0
		inputs = []
		
		try:
			if(self.wallet.balance() < amount):
				raise Exception("Not enough money!")
			key = sender_public
			for utxo in self.wallet.utxos[key]:
				sum = sum + utxo['amount']
				inputs.append(utxo['id'])
				if (sum >= amount):
					break
			trxn = copy.deepcopy(transaction.Transaction(sender_public, senderID, receiver_public, receiverID, amount, inputs))
			trxn.sign_transaction(self.wallet.private_key) #set id & signature
			trxn.transaction_outputs.append({'id': trxn.id, 'to_who': trxn.sender, 'amount': sum-trxn.amount})
			trxn.transaction_outputs.append({'id': trxn.id, 'to_who':trxn.receiver, 'amount': trxn.amount})

			if(self.validate_transaction(self.wallet.utxos,trxn) == 'validated'): # Node validates the trxn it created
				self.add_transaction_to_validated(trxn)
				self.broadcast_transaction(trxn)
				return "Created new transaction!"
			else:
				return "Transaction not created,error"
		
		except Exception as e:
			print(f"create_transaction: {e.__class__.__name__}: {e}")
			return "Not enough money!"

	# does not change lists of validated or pending transactions, only returns code
	def validate_transaction(self, wallet_utxos, t): 
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
					print('Missing transaction inputs')
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


	# check if any of the pending transactions can be validated
	# if it can be validated, remove it from pending and added to validated
	def validate_pending(self):
		print("validate_pending")
		for t in self.pending_trans:
			if validate_transaction(self.wallet.utxos, t) == 'validated':
				self.pending_trans.remove(t)
				self.add_transaction_to_validated(t)


	def add_transaction_to_pending(self, t):
		print("add_transaction_to_pending")
		self.pending_trans.append(t)


	# comparing transaction objects
	def remove_from_old_valid(self, to_remove):
		print("remove_from_old_valid")
		tmp = [trans for trans in self.old_valid if trans not in to_remove]
		self.old_valid = tmp

	# add transaction to list of valid_trans
	# call mine if it is full
	# return True if mining was trigerred, else False
	def add_transaction_to_validated(self, transaction):
		global CAPACITY
		print("add_transaction_to_validated")
		self.valid_trans.append(transaction)
		self.old_valid.append(transaction)
		if len(self.valid_trans) == CAPACITY:
			tmp = copy.deepcopy(self.valid_trans) 					# create a new block out of the valid transactions
			self.valid_trans = []									# reinitialize the valid transactions list
			future = self.pool.submit_task(self.init_mining, tmp, copy.deepcopy(self.wallet.utxos))
			print(str(os.getpid()) + ' assigned it to mining thread')
			return True				
		else:
			return False


	def receive_block(self, block):
		print("receive_block")
		tmp_utxos = copy.deepcopy(self.wallet.utxos_snapshot)
		if self.block_REDO(block, tmp_utxos):
			lock.acquire()
			if self.validate_block(block):
				print("___VALID BLOCK RECEIVED___")
				self.valid_chain.add_block(block)
				lock.release()
				
				# UPDATE LISTS
				# delete from my pending what was in block
				new_pending = [trans for trans in self.pending_trans if trans not in block.listOfTransactions]
				self.pending_trans = new_pending
				
				# add to my unreceived
				new_unreceived = [trans for trans in block.listOfTransactions if trans not in (self.old_valid and self.pending_trans)]
				for t in new_unreceived:
					self.unreceived_trans.append(t)
				
				# update validated trans
				new_valid = [trans for trans in self.old_valid if trans not in block.listOfTransactions]
				self.valid_trans = new_valid
				self.remove_from_old_valid(block.listOfTransactions)
				self.wallet.utxos_snapshot = copy.deepcopy(tmp_utxos)
				self.wallet.utxos = copy.deepcopy(tmp_utxos)
			
			else:
				lock.release()
				self.resolve_conflict()
		else:
			print("__BLOCK REDO FAILED__")
			self.resolve_conflict()



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
		print("________KNOCK KNOCK KNOCKING ON HEAVEN'S DOOR________")
		while guess[:difficulty]!=('0'*difficulty):
			block.nonce += 1
			guess = block.myHash()
		block.hash = guess
		print('Mining succeded by{}'.format(threading.current_thread()))
		return

	# [THREAD]	
	def validate_block(self, block):
		print("validate_block")
		return block.previousHash == self.valid_chain.block_list[-1].hash and block.hash == block.myHash()


	# [THREAD] create block and call mine
	def init_mining(self, valid_trans, current_utxos):
		print("init_miner")
		print('Task Executed {}'.format(threading.current_thread()))
		newBlock = self.create_new_block(valid_trans)
		shared = [t for t in newBlock.listOfTransactions if t in self.valid_chain.block_list[-1].listOfTransactions]
		if (shared):
			print("Stopping mining, block already added")
			return

		self.mine_block(newBlock)
		lock.acquire()
		# ----- LOCK ----------
		if self.validate_block(newBlock):
			print('***Mined block valida will be broadcasted')
			self.valid_chain.add_block(newBlock)
			self.remove_from_old_valid(valid_trans)
			self.wallet.utxos_snapshot = current_utxos
		# ----- UNLOCK --------
			lock.release()
			self.broadcast_block(newBlock)
		else:
			lock.release()
			print('***Mined block invalida will not be broadcasted')
		return


	#Consensus functions

	# redo all the transactions in a block
	def block_REDO(self, block, utxos):
		for trans in block.listOfTransactions:
			if (self.validate_transaction(utxos, trans) != 'validated'):
				return False
		return True

	# validate chain's hashes
	def chain_hashes_validation(self,chain):
		prev_hash = chain[0].hash
		for b in chain[1:]:
			if(b.previousHash != prev_hash or b.hash != b.myHash()):
				return False
			prev_hash = b.hash
		return True

	# validates and returns list of block objects
	def validate_chain(self, blocklist):
		print("__validate chain__")
		print("__________I CAN STILL HEAR YOU SAYING__________")
		
		chain = []
		# initialize pending and unreceived transactions
		pending = copy.deepcopy(self.pending_trans) # we will use these lists just for validation and
		valid = copy.deepcopy(self.valid_trans)
		pending += valid
		unreceived = copy.deepcopy(self.unreceived_trans)	# then we will add them to node's lists
		tmp_utxos = {}
		# REDO bootstrap's utxos which are not validated
		btstrp_public_k = self.ring[0]['public_key']
		amount = len(self.ring.keys())*100 # number of nodes * 100 NBCs
		tmp_utxos[btstrp_public_k] = [{"id":0,"to_who":btstrp_public_k,"amount":amount}]

		self.add_block_list_to_chain(chain,blocklist) # to convert dictionaries to block Objects

		if not self.chain_hashes_validation(chain):
			print("CHAIN HAS INVALID HASHES")
			return False
			
		# i is our old block, j the block from new blockchain
		for i, j in zip(self.valid_chain.block_list[1:], chain[1:]):
			print("CHECKING HASHES:::::")
			print(i.hash)
			print("~~~~~~~~~~~~~")
			print(j.hash)
			old_trans = i.listOfTransactions
			new_trans = j.listOfTransactions
			A = [t for t in old_trans if t not in new_trans]
			B = [t for t in new_trans if t not in old_trans]
			# if pending transactions in new block, remove them, and add pending from i
			tmp_pending = [t for t in pending if t not in B] + [t for t in A if t not in unreceived]
			# if unreceived transactions in i, remove them, and add unreceived from j
			tmp_unreceived = [t for t in unreceived if t not in A] + [t for t in B if t not in pending]

			# REDO block and check its validity
			if( not self.block_REDO(j,tmp_utxos)):
				print("Chain invalid!")
				return False

			pending = tmp_pending
			unreceived = tmp_unreceived

		# validation successfull
		self.pending_trans = copy.deepcopy(pending)
		self.unreceived_trans = copy.deepcopy(unreceived)
		print(self.pending_trans)
		print(self.unreceived_trans)

		return True, chain, tmp_utxos


	def resolve_conflict(self):
		#resolve correct chain
		print("resolve_conflicts")
		print('IMAGINE ALL THE PEOPLE')
		print('\t\t\tLIVING LIFE IN PEEEEEEACE')
		max_length = len(self.valid_chain.block_list)
		max_id = self.id
		max_ip= self.ring[max_id]['ip']
		max_port= self.ring[max_id]['port']
		#check if someone has longer block chain
		print("_____my block hashes are_____")
		for b in self.valid_chain.block_list:
			print(b.hash,"->")
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
			valid, new_blockchain, new_utxos = self.validate_chain(received_blocklist)
			if not valid:
					raise Exception('received invalid chain')
			
			# Validate all transactions in confirmed blockchain
			self.wallet.utxos = copy.deepcopy(new_utxos)
			self.wallet.utxos_snapshot = copy.deepcopy(new_utxos)
			self.valid_chain.block_list = new_blockchain
			print("__Conflict resolved successfully!__")
			print("__________SO SALLY CAN WAIT__________")
		except Exception as e:
			print(f'consensus.{n_id}: {e.__class__.__name__}: {e}')