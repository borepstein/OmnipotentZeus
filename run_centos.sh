#!/bin/bash

yum groupinstall 'Development Tools' -y
yum install epel-release -y
wget http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm
rpm -ivh epel-release-7-8.noarch.rpm
yum install mysql-community-server -y
yum install mysql-devel
yum install git vim screen python-pip mysql-server mysql-devel.x86_64 python-devel python-lxml libaio* gcc wget make libibverbs.x86_64 -y
pip install mysql-python
pip install sqlalchemy
screen python OmnipotentZeus/hermes.py