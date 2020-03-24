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
	def create_blockchain(self):
		genesis = block.Block(previousHash=1)
		genesis.nonce=0
		genesis.myHash()
		self.block_list.append(genesis)
		return

	#add _validated_ block to blockchain by miners
	def add_block(self,new_block):
		self.block_list.append(new_block)