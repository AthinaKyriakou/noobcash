from collections import OrderedDict

import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import node
import block
import copy
import transaction
import requests
from flask import Flask, jsonify, request, render_template


class Blockchain:

	def __init__(self):
		##set
		self.block_list = []
		
	# create bootstrap_node and 
	# genesis block(previous_hash = 1, nonce = 0)
	def create_blockchain(self, genesis_trans):
		genesis = block.Block(index = 0, previousHash = 1)
		genesis.listOfTransactions.append(genesis_trans)
		genesis.hash = genesis.myHash()
		self.add_block(genesis) # only genesis block is added instantly to blockchain
		return


	def print_chain(self):
		print("\n___PRINT CHAIN___")
		for b in self.block_list:
			b.print_block()


	# add to chain 
	def add_block(self, new_block):
		# print("add_block")
		self.block_list.append(new_block)
		self.print_chain()
		print('length: \t' + str(len(self.block_list)))

