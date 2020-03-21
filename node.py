import block
import wallet

MINING_DIFFICULTY = 5
init_count = -1 #initial id count, accept ids <= 10

class Node:
	def __init__(self,NUM_OF_NODES=None):
		global init_count
		self.NBC=100;
		##set
		print("node_init")
		self.wallet=wallet.Wallet()
		self.id=-1 # bootstrap will send the node's final ID
		# self.valid_chain

		# NUM_OF_NODES has value only for bootstrap node
		# # each other node that connects to network gets initialized by bootstrap
		# if(NUM_OF_NODES!=None):	
		# 	if(init_count < NUM_OF_NODES):
		# 		init_count+=1
		# 		self.id = init_count


		# self.NBCs

		#self.ring[]   #here we store information for every node, as its id, its address (ip:port) its public key and its balance 




	def create_new_block():
		print("create_block")
	def create_wallet():
		#create a wallet for this node, with a public key and a private key
		print("create_wallet")
	def register_node_to_ring():
		#add this node to the ring, only the bootstrap node can add a node to the ring after checking his wallet and ip:port address
		#bottstrap node informs all other nodes and gives the request node an id and 100 NBCs
		print("register_node")

	def create_transaction(sender, receiver, signature):
		#remember to broadcast it
		print("create_transaction")

	def broadcast_transaction():
		print("broadcast_transaction")




	def validdate_transaction():
		#use of signature and NBCs balance
		print("validdate_transaction")

	def add_transaction_to_block():
		#if enough transactions  mine
		print("add_transaction_to_block")


	def mine_block():
		print("mine_block")


	def broadcast_block():
		print("broadcast_block")

		

	def valid_proof(other_parameters, difficulty=MINING_DIFFICULTY):
		print("valid_proof")



	#concencus functions

	def valid_chain(self, chain):
		#check for the longer chain accroose all nodes
		print("valid_chain")

	def resolve_conflicts(self):
		#resolve correct chain
		print("resolve_conflicts")


