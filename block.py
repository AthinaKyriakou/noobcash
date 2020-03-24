import blockchain
import datetime;
from collections import OrderedDict
import json

class Block:
	def __init__(self, **kwargs):
		##set
		print('block_init')
		self.previousHash=kwargs['previousHash']
		self.timestamp=datetime.datetime.now().timestamp()
		self.nonce=kwargs['nonce']
		self.listOfTransactions=[]

		#calculate self.hash
		hash_data = OrderedDict([('prev':self.previousHash),('tmsp':self.timestamp), ('nonce': self.nonce)])
		tmp = json.dumps(hash_data) 
		self.hash = SHA384.new(tmp.encode())


