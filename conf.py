# CONFIGURATION INFORMATION

# DATABASE CREDENTIALS
db_host = "HOST"
db_user = "USERNAME"
db_password = "PASSWORD"
db_name = "DATABASE"

# PROJECT DETAILS
project_id = 'c-edgehosting-20161107'  # Start date format is YYYYMMDD (e.g., 20170130 for January 30TH, 2017)
operating_system = 'ubuntu'  # Please enter the operating system (ubuntu or centos)

# TESTS TO RUN
# Please mark with a y (indicating yes) for each test you want to run
geekbench = 'y'  # System test
iperf = 'y'  # Internal network test
fio = 'y'  # Disk test
iozone = 'n'  # Disk test
sysbench = 'n'  # Disk test
apachebench = 'n'  # Apachebench test
spec = 'n'  # System test

# DISK TEST INFORMATION
blocksize = '4'  # Block size in kilobytes
filesize = '16'  # File size in megabytes
runtime = '60'  # How long would you like this test to run for (in seconds)
direct_io = 'y'  # If direct I/O is required (bypass cache), please mark y
async_io = 'y'  # Set y to enable asynchronous tests

# INTERNAL NETWORK INFORMATION
internal_net_time = '60'  # time (in seconds) that you want iperf to run

# APACHE BENCH
ab_requests = "200"  # Number of requests to perform
ab_concurrency = "10"  # Number of multiple requests to make at a time
ab_timeout = "30"  # Maximum seconds to wait for each response. default 30s.
ab_hostname = "104.131.118.115"  # Hostname
ab_port = ""  # Default port 80
ab_path = "/admin"  # Path

# TIMING
# Either duration or number of iterations must complete in order for the testing to stop.
sleeptime = 0  # Adjust the time in between iterations, input a sleeptime (in seconds).
iterations = 10000  # Specify the number of iterations this testing should complete,
duration = 24  # Duration and duration value will limit the time the suite will be running for.
duration_value = "hours"  # Please enter seconds, minutes, hours, or days

if duration_value.lower() == "seconds":
    duration = duration
elif duration_value.lower() == "minutes":
    duration = duration * 60
elif duration_value.lower() == "hours":
    duration = duration * 3600
elif duration_value.lower() == "days":
    duration = duration * 86400

# GEEKBENCH LICENSE
# Email and Key for unlocking the Geekbench license
gb_email = 'contact@cloudspectator.com'
gb_key = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'
