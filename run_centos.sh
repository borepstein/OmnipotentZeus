yum install epel-release -y
yum install screen python-pip mysql-server mysql-devel.x86_64 python-devel python-lxml libaio* gcc wget make libibverbs.x86_64 -y
pip install mysql-python
pip install sqlalchemy
pip install beautifulsoup4
screen python OmnipotentZeus/hermes.py