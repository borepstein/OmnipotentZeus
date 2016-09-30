import pymysql

db_host = "104.131.53.14"
db_user = "remote"
db_password = "800BoylstonClouds"
db_name = "forecast"

con = pymysql.connect(db_host, db_user, db_password, db_name)
cur = con.cursor(pymysql.cursors.DictCursor)

lst = ['t2.nano',
       't2.micro',
       't2.small',
       't2.medium',
       't2.large',
       'm4.large',
       'm4.xlarge',
       'm4.2xlarge',
       'm4.4xlarge',
       'm4.10xlarge',
       'm3.medium',
       'm3.large',
       'm3.xlarge',
       'm3.2xlarge',
       'c4.large',
       'c4.xlarge',
       'c4.2xlarge',
       'c4.4xlarge',
       'c4.8xlarge',
       'c3.large',
       'c3.xlarge',
       'c3.2xlarge',
       'c3.4xlarge',
       'c3.8xlarge',
       'x1.32xlarge',
       'r3.large',
       'r3.xlarge',
       'r3.2large',
       'r3.4large',
       'r3.8large',
       'i2.large',
       'i2.xlarge',
       'i2.2large',
       'i2.4large',
       'i2.8large',
       'd2.large',
       'd2.xlarge',
       'd2.2large',
       'd2.4large',
       'd2.8large',
       ]

for i in lst:
    for j in range(1, 4):
        q = "INSERT INTO xiaoice_virtualmachine (`key`, display, location_id, provider_id) VALUES ('%s', '%s', %s, %s)" % (i, i, j, 1)
        cur.execute(q)
        con.commit()
