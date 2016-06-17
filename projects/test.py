# CONFIGURATION INFORMATION

# Please enter the start date for this test in YYYYMMDD (e.g., 20160617 for June 17TH, 2016)
project_id = 'c-edgehosting-20151210'
# Please enter the operating system
operating_system = 'windows'  # windows

# TESTS TO RUN
# Please mark with a y (indicating yes) for each test you want to run
geekbench = 'y'  # system tests
iperf = 'y'  # Internal network tests
fio = 'y'  # disk tests

iozone = 'n'  # disk tests
sysbench = 'n'  # disk tests
passmark = 'n'  # disk tests

# DISK TEST INFORMATION
# If you selected yes for disk tests, then you have to fill out this information
blocksize = '4'  # please enter the block size in kilobytes
filesize = '16'  # please enter the file size in megabytes
numjobs = '8'  # please enter the number of copies of the test that you would like to run
runtime = '60'  # how long would you like this test to run for in seconds
direct_io = 'y'  # if direct I/O is required (bypass cache), please mark y
async_io = 'y'  # Set y to enable asynchronous tests

# INTERNAL NETWORK INFORMATION
# If you selected yes for internal network tests, then you have to fill out this information
internal_net_time = '60'  # please enter the time, in seconds, that you want iperf to run

# TIMING
# Timing variables to help keep the sequence of events.
# To adjust the time in between runs, input a sleeptime (in seconds).
# To specify the number of iterations this testing should complete, please input an integer for iterations.
# Duration and duration value will limit the time the suite will be running for.
# Either duration or number of iterations must complete in order for the testing to stop.
sleeptime = 0
iterations = 1
duration = 15
duration_value = "minutes"  # please enter seconds, minutes, hours, or days
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
geekbench_install_dir = 'C:\Program Files (x86)'
fio_install_dir = 'C:\Program Files (x86)'
iozone_install_dir = 'C:\Program Files (x86)\Benchmarks\Iozone3_414'
passmark_install_dir = 'C:\Program Files (x86)'
