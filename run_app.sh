#!/bin/sh
cd ~/noobcash
export FLASK_APP=rest.py
export FLASK_DEBUG=rest.py
flask run --host=0.0.0.0
