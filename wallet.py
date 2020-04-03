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

	def __init__(self, utxos={}):
		##set
		rsa_key = RSA.generate(1024)
		self.private_key = rsa_key.exportKey('PEM').decode()
		self.public_key = rsa_key.publickey().exportKey('PEM').decode()
		self.utxos = utxos #key : public key, value: {id, to_who, amount}
		self.utxos_snapshot = {} # we will use it to validate any received block


	def balance(self):
		temp=self.public_key
		sum=0
		for i in self.utxos[temp]:
			sum=sum+i['amount']
		return sum
