#!/bin/bash

func=$1
port=$2

if [ "$#" -lt 2 ]
then
	echo "$(tput setaf 6)Usage: ./setup.sh <action/help> $(tput bold)PORT$(tput sgr0)"
else
	case $func in
		run)
			pip install termcolor
			pip install flask_cors
			export FLASK_APP=rest.py
			export FLASK_DEBUG=1
			flask run --host=0.0.0.0 --port=$port
			;;
		init)
			if [ "$#" -ne 3 ]
			then
				echo "$(tput setaf 6)Usage: ./setup.sh init $(tput bold)PORT num_of_nodes$(tput sgr0)"
			else
				num_of_nodes=$3
				curl http://localhost:$port/init/$num_of_nodes
			fi
			;;
		connect)
			if [ "$#" -ne 3 ]
			then
				echo "$(tput setaf 6)Usage: ./setup.sh connect $(tput bold)PORT IP$(tput sgr0)"
			else
				ip=$3
				curl http://localhost:$port/connect/$ip/$port
			fi
			;;
		# testing)
		# 	if [ "$#" -ne 4 ]
		# 	then
		# 		echo "$(tput setaf 6)Usage: ./setup.sh testing $(tput bold)PORT num_of_nodes ID $(tput sgr0)"
		# 	else
		# 		num_of_nodes=$3
		# 		id=$4
		# 		file="transactions$id.txt"
		# 		input="transactions/${num_nodes}nodes/$file"
		# 		while IFS= read -r line
		# 		do
		# 			echo $line
		# 			sender_id=cut -d" " 1 $line
		# 			amount=cut -d" " 2 $line
		# 		done < $input
		# ;;
		*)
	esac
fi

