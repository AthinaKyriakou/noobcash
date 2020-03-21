import binascii

import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

import hashlib
import json
from time import time
from urllib.parse import urlparse
from uuid import uuid4



class Wallet:

	def __init__(self):
		##set
		print("wallet_init")
		rsa_key = RSA.generate(1024)
		self.private_key = rsa_key.exportKey('PEM').decode()
		self.public_key = rsa_key.publickey().exportKey('PEM').decode()

		#self.address
		#self.transactions

	def balance():
		print("balance")