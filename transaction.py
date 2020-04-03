from collections import OrderedDict

import binascii
import Crypto
import Crypto.Random
from Crypto.Hash import SHA
from Crypto.Hash import SHA384
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
import base64
import json

import requests
from flask import Flask, jsonify, request, render_template


class Transaction:

    def __init__(self, sender, senderID, receiver, receiverID, amount, transaction_inputs, transaction_outputs = [], id = None, signature = None):
        ##set
        self.sender = sender                                # public key str
        self.receiver = receiver                            # public key str
        self.senderID = senderID                            # ring IDs int
        self.receiverID = receiverID
        self.amount = amount                                # int
        self.id = id                                        # transaction hash (str)
        self.transaction_inputs = transaction_inputs        # list of int
        self.transaction_outputs = transaction_outputs      # list of dicts
        self.signature = signature


    # 2 transactions are equal when they have the same hash (compare 2 strings)
    def __eq__(self, other):    
        if not isinstance(other, Transaction):
            return NotImplemented
        return self.id == other.id

    def to_dict(self):
        return OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount), ('transaction_inputs', self.transaction_inputs), ('transaction_outputs', self.transaction_outputs), ('id', self.id), ('signature', self.signature)])

    def hash(self):
        trans = OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount), ('transaction_inputs', self.transaction_inputs)])
        temp=json.dumps(trans) 
        return SHA384.new(temp.encode())

    def sign_transaction(self, sender_private_key):
        hash_obj = self.hash() 
        private_key = RSA.importKey(sender_private_key) 
        signer = PKCS1_v1_5.new(private_key)
        self.id = hash_obj.hexdigest() 
        self.signature = base64.b64encode(signer.sign(hash_obj)).decode()
        return self.signature
 
    def verify_signature(self):
        #Verifies with a public key from whom the data came that it was indeed 
        #signed by their private key
        rsa_key = RSA.importKey(self.sender.encode()) #sender public key
        verifier = PKCS1_v1_5.new(rsa_key) 
        hash_obj = self.hash()
        return verifier.verify(hash_obj, base64.b64decode(self.signature)) #signature needed to be decoded