import blockchain
import datetime;

class Block:
	def __init__(self, previousHash, nonce):
		##set
		print("block_init")
		self.previousHash=previousHash
		self.timestamp=datetime.datetime.now().timestamp()
		self.nonce=nonce
		self.listOfTransactions=[]
		#calculate self.hash
		hash_data = {'prev':self.previousHash,'tmsp':self.timestamp, 'nonce': self.nonce}
		tmp = json.dumps(trans) 
        self.hash = SHA384.new(tmp.encode())
	
	# def myHash():
	# 	#calculate self.hash
	# 	print("myHash")
	# 	hash_data = {'prev':self.previousHash,'tmsp':self.timestamp, 'nonce': self.nonce}
	# 	tmp = json.dumps(trans) 
 #        self.hash = SHA384.new(tmp.encode())