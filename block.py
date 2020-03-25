import blockchain
import datetime;
from collections import OrderedDict
from Crypto.Hash import SHA256
import json

class Block:
	def __init__(self, index = -1, previousHash = None):
		##set
		print('block_init')
		self.index = index
		self.previousHash = previousHash
		self.timestamp = datetime.datetime.now().timestamp()
		self.nonce = 0
		self.listOfTransactions=[]
		self.hash = None

	def myHash(self):
		print("myHash")
		hash_data = OrderedDict([('prev',self.previousHash),('tmsp',self.timestamp), ('nonce',self.nonce),('transactions',self.listOfTransactions)])
		tmp = json.dumps(hash_data)
		self.hash = SHA256.new(tmp.encode())
		return
