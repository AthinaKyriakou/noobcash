from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import node
import block
import transaction
import requests
from flask import Flask, jsonify, request, render_template


class Blockchain:

	def __init__(self):
		##set
		print('blockchain_init')
		self.block_list = []
		
	# create bootstrap_node and 
	# genesis block(previous_hash = 1, nonce = 0)
	def create_blockchain(self, genesis_trans):
		genesis = block.Block(index = 0, previousHash = 1)
		genesis.listOfTransactions.append(genesis_trans)
		genesis.myHash()
		self.block_list.add_block(genesis) # only genesis block is added instantly to blockchain
		return

	# check if block is the first received
	#FILLME
	def is_first_received_block(self, new_block):
		if True:
			self.add_block(new_block)


	# add to chain 
	def add_block(self, new_block):
		self.block_list.append(new_block)