#!/bin/bash

function=$1

echo "$(tput setaf 6)Enter <help> for options"
echo "<Running: "$function">$(tput sgr0)"

functions=( "init" "connect" "new_transaction" "view_transactions" "balance" )

expl=('initialize network with bootstrap node'
		'connect node to network'
		'create a transaction'
		"view transactions in last validated block"
		"view node\'s balance")

use=('use: ./examples.sh init <number of nodes>'
	'use: ./examples.sh connect <IP> <PORT>'
	'use ./examples.sh new_transaction <REC_IP>:<REC_PORT> <amount>'
	'use ./examples.sh view_transactions <PORT>'
	'use ./examples.sh balance <PORT>')

case $function in
	init)
		num_of_nodes=$2
		# use: ./examples.sh init <number of nodes>
		curl http://localhost:5000/init/$num_of_nodes
		;;
	connect)
		ip=$2
		port=$3
		# use: ./examples.sh connect <IP> <PORT>
		curl http://localhost:$port/connect/$ip/$port
		;;
	new_transaction)
		port=$2
		recipient=$3 # in <IP>:<PORT> format
		amount=$4
		data='{"recipient":${recipient},"amount":${amount}}'
		# use ./examples.sh new_transaction <REC_IP>:<REC_PORT> <amount>
		curl data -X POST http://localhost:$port/transaction/new
		;;
	view_transactions)
		port=$2
		# use ./examples.sh view_transactions <PORT>
		curl http://localhost:$port/transactions/view
		;;
	balance)
		port=$2
		# use ./examples.sh balance <PORT>
		curl http://localhost:$port/balance
		;;
	help)
		for i in {0..4}
		do
			echo "$(tput setaf 3)"
			echo "$(tput setaf 6)${functions[$i]}$(tput setaf 3):  ${expl[$i]}"
			echo "${use[$i]}"
			echo "$(tput setaf 4)~~~~~~~~~~"
		done
		;;
	*)
esac
echo "$(tput setaf 6)<Done>$(tput sgr0)"