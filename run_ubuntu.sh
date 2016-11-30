#!/bin/bash

apt-get update

apt-get install screen python-pip libmysqlclient-dev python-dev python-lxml --yes
pip install -r requirements.txt
python base.py