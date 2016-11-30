#!/bin/bash

yum groupinstall 'Development Tools' -y
yum install epel-release -y
wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm
rpm -ivh epel-release-7-8.noarch.rpm

yum install screen python-pip python-devel python-lxml libaio* wget libibverbs.x86_64 -y
pip install -r requirements.txt
python base.py