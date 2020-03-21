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

    def __init__(self, sender, sender_privkey, recipient, value, input, id=None, signature=None):
        ##set
        print("transaction_init")
        self.sender = sender #public key του wallet από το οποίο προέρχονται τα χρήματα
        self.receiver = recipient #public key του wallet στο οποίο θα καταλήξουν τα χρήματα
        self.amount = value #: το ποσό που θα μεταφερθεί
        self.id = id #: το hash του transaction
        self.transaction_inputs = input #: λίστα από Transaction Input . previousOutputId
        self.transaction_outputs = [] #: λίστα από Transaction Output 
        self.signature=signature		
        self.sender_privkey = sender_privkey


    def to_dict(self):
        print("to_dict")
        return OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount), ('transaction_inputs', self.transaction_inputs), ('transaction_outputs', self.transaction_outputs), ('id', self.id), ('signature', self.signature)])
    
    def hash(self):
        trans = OrderedDict([('sender', self.sender), ('receiver', self.receiver), ('amount', self.amount), ('transaction_inputs', self.transaction_inputs)])
        temp=json.dumps(trans) 
        return SHA384.new(temp.encode()) #κρυπογραφεί τα στοιχεία του transaction που είναι σε utf8

    def sign_transaction(self):
        """
        Sign transaction with private key
        """
        print("sign_transaction")
        hash_obj = self.hash() 
        private_key = RSA.importKey(self.sender_privkey) 
        signer = PKCS1_v1_5.new(private_key)
        self.id = hash_obj.hexdigest() #SET ID. This is an object from the Crypto.Hash package. It has been used to digest the message to sign. safer as a hex
        self.signature = base64.b64encode(signer.sign(hash_obj)).decode() #ισως να μπορουμε και με binascii. not sure why encoding&decoding is needed
        print("sig:", self.signature)
        return self.signature