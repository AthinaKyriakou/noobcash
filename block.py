import blockchain
import datetime;
from collections import OrderedDict

class Block:
	#def __init__(self, previousHash, nonce):	# to be used once implemented
	def __init__(self):
		##set
		print('block_init')
		#self.previousHash=previousHash
		self.timestamp=datetime.datetime.now().timestamp()
		#self.nonce=nonce
		self.listOfTransactions=[]
		#calculate self.hash
		hash_data = OrderedDict([('prev', self.previousHash),('tmsp', self.timestamp), ('nonce', self.nonce)])
		tmp = json.dumps(hash_data) 
		self.hash = SHA384.new(tmp.encode())
	
	# def myHash():
	# 	#calculate self.hash
	# 	print("myHash")
	# 	hash_data = {'prev':self.previousHash,'tmsp':self.timestamp, 'nonce': self.nonce}
	# 	tmp = json.dumps(trans) 
 #        self.hash = SHA384.new(tmp.encode())