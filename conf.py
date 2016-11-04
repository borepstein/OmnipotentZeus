# DATABASE CREDENTIALS
db_host = "localhost"
db_user = "root"
db_password = "inapp"
db_name = "forecast"

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
iterations = 2
sleep_time = 0  # in seconds
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
gb_email = 'contact@cloudspectator.com'
gb_key = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'

# GEEKBENCH DIRECTORY
geekbench_install_dir = "dist/Geekbench-3.1.2-Linux"
