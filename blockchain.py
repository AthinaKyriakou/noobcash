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
		print("blockchain_init")
		self.block_list = []
		
	#create bootstrap_node and genesis block
	def create_blockchain(self,NUM_OF_NODES):
		genesis = block.Block()
		self.block_list.append(genesis)
		genesis_tans=transaction() # add parameters for init

	#add _validated_ block to blockchain by miners
	def add_block(self,new_block):
		self.block_list.append(new_block)