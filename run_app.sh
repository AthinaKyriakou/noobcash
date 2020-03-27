#!/bin/sh

if [ "$#" -ne 1 ]
then
	echo "$(tput setaf 6)Usage: ./run_app.sh $(tput bold)PORT$(tput sgr0)"
else
	port=$1
	export FLASK_APP=rest.py
	export FLASK_DEBUG=rest.py
	flask run --host=0.0.0.0 --port=$port
fi