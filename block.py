import blockchain
import datetime;
from collections import OrderedDict
from Crypto.Hash import SHA384
import json

class Block:
	def __init__(self, previousHash=None):
		##set
		print('block_init')
		self.previousHash=previousHash
		self.timestamp=datetime.datetime.now().timestamp()
		self.nonce=None
		self.listOfTransactions=[]
		self.hash = None

	def myHash(self):
		print("myHash")
		hash_data = OrderedDict([('prev',self.previousHash),('tmsp',self.timestamp), ('nonce',self.nonce)])
		tmp = json.dumps(hash_data) 
		self.hash = SHA384.new(tmp.encode())
		return
