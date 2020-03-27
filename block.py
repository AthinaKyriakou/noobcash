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

	def listToSerialisable(self):
		final = []
		for trans in self.listOfTransactions:
			final.append(trans.__dict__)
		return final

	def myHash(self):
		hash_data = OrderedDict([('index',self.index),('prev',self.previousHash),('tmsp',self.timestamp), ('nonce',self.nonce),('transactions',self.listToSerialisable())])
		tmp = json.dumps(hash_data)
		return SHA256.new(tmp.encode()).hexdigest()
