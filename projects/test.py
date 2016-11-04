# CONFIGURATION INFORMATION

# DATABASE CREDENTIALS
db_host = "localhost"
db_user = "root"
db_password = "inapp"
db_name = "omnipotentzeuslinux"

# Please enter the start date for this test in YYYYMMDD (e.g., 20150115 for January 15TH, 2015)
project_id = 'c-edgehosting-20161104'
# Please enter the operating system
operating_system = 'ubuntu'  # debian, ubuntu, redhat, or centos

# TESTS TO RUN
# Please mark with a y (indicating yes) for each test you want to run
geekbench = 'y'  # system tests
iperf = 'y'  # internal network tests
fio = 'y'  # disk tests
iozone = 'y'  # disk tests
sysbench = 'y'  # disk tests
apachebench = 'y'  # apachebench tests

# DISK INFORMATION
# If you selected yes for disk_rand or disk_seq, then you have to fill out this information
blocksize = '4'  # please enter the block size in kilobytes
filesize = '16'  # please enter the file size in megabytes
numjobs = '8'  # please enter the number of copies of the test that you would like to run
runtime = '60'  # how long would you like this test to run for in seconds
direct_io = 'y'  # if direct I/O is required (bypass cache), please mark y
async_io = 'y'  # Set y to enable asynchronous tests

# INTERNAL NETWORK INFORMATION
# If you selected yes for internal network tests, then you have to fill out this information
internal_net_time = '60'  # please enter the time, in seconds, that you want iperf to run

# APACHE BENCH
ab_requests = "200"  # number of requests to perform
ab_concurrency = "10"  # number of multiple requests to make at a time
ab_timeout = "30"  # maximum seconds to wait for each response. default 30s.
ab_hostname = "104.131.118.115"  # hostname
ab_port = ""  # default port 80
ab_path = "/admin"  # path

# TIMING
# Timing variables to help keep the sequence of events.
# To adjust the time in between runs, input a sleeptime (in seconds).
# To specify the number of iterations this testing should complete, please input an integer for iterations.
# Duration and duration value will limit the time the suite will be running for.
# Either duration or number of iterations must complete in order for the testing to stop.
sleeptime = 0
iterations = 5000000
duration = 24
duration_value = "hours"  # please enter seconds, minutes, hours, or days

if duration_value.lower() == "seconds":
    duration = duration
elif duration_value.lower() == "minutes":
    duration = duration * 60
elif duration_value.lower() == "hours":
    duration = duration * 3600
elif duration_value.lower() == "days":
    duration = duration * 86400

# GEEKBENCH LICENSE
# Email and Key for unlocking the license
email = 'contact@cloudspectator.com'
key = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'

# DIRECTORY
# The directory that houses the Geekbench 3 suite and where all the tests will run
geekbench_install_dir = "dist/Geekbench-3.1.2-Linux"
