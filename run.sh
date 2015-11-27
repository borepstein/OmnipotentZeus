apt-get update
apt-get install python-pip mysql-server libmysqlclient-dev python-dev python-lxml --yes
pip install -y mysql-python
pip install -y sqlalchemy
pip install -y beautifulsoup4
screen python OmnipotentZeus/hermes.py
