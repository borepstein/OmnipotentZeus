apt-get update
apt-get install python-pip mysql-server libmysqlclient-dev python-dev python-lxml --yes
pip install -r requirements.txt
python hermes.py
