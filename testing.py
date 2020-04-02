import os
import sys
import numpy as np

if __name__ == '__main__':

	if(len(sys.argv) != 4):
		print("Usage: python testing.py <PORT> <ID> <num_of_nodes>")
		exit()	
	port = sys.argv[1]
	myID = sys.argv[2]
	num_nodes = sys.argv[3]

	file = f'transactions/{num_nodes}nodes/transactions{myID}.txt'
	f = open(file,"r")
	lines = f.readlines() # comment out to run all lines

	# for line in f: # uncomment
	for line, i in zip(lines, np.arange(10)):  # comment out
		print(f'executing line {line}')
		id, amount = line.split()
		id = id[-1]
		os.system(f'./examples.sh new_transaction {port} {id} {amount}')
