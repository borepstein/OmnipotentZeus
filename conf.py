# CONFIGURATION INFORMATION

# DATABASE CREDENTIALS
db_host = "HOST"
db_user = "USERNAME"
db_password = "PASSWORD"
db_name = "DATABASE"

# Operating System
operating_system = "ubuntu"

# TESTS TO RUN
geekbench = 'y'  # system tests
fio = 'y'  # disk tests
iperf = 'y'  # internal network tests

# DISK INFORMATION
blocksize = '4'  # please enter the block size in kilobytes
filesize = '16'  # please enter the file size in megabytes
numjobs = '8'  # please enter the number of copies of the test that you would like to run
runtime = '60'  # how long would you like this test to run for in seconds
direct_io = 'y'  # if direct I/O is required (bypass cache), please mark y

# INTERNAL NETWORK INFORMATION
internal_net_time = '60'  # please enter the time, in seconds, that you want iperf to run

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
gb_email = 'contact@cloudspectator.com'
gb_key = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'
