apt-get update
apt-get install python-pip mysql-server libmysqlclient-dev python-dev python-lxml --yes
pip install mysql-python
pip install sqlalchemy
pip install beautifulsoup4
screen python hermes.py