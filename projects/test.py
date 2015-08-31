# TESTS TO RUN
# CONFIGURATION INFORMATION

from datetime import datetime

project_id = 'aws-%s' % datetime.now().strftime('%Y%m%d')
startdate_input = datetime.now().strftime('%Y%m%d-%H%M')  # Please enter the start date for this test in YYYYMMDD (e.g., 20150115 for January 15TH, 2015)
operating_system = 'windows'  # windows

# Please mark with a y (indicating yes) for each test you want to run
system_tests = 'y'  # Geekbench 3 suite
disk_rand = 'y'  # sqlio random read and random write
disk_seq = 'y'  # sqlio sequential read and sequential write
internal_net_tests = 'y'  # iperf internal network tests

# INTERNAL NETWORK INFORMATION
# If you selected yes for internal network tests, then you have to fill out this information
internal_net_time = '60'  # Please enter the time, in seconds, that you want iperf to run

# TIMING
# Timing variables to help keep the sequence of events. To adjust the time in between runs, input a sleeptime (in seconds). 
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

textnotifications = 'n'

# GEEKBENCH LICENSE
# Email and Key for unlocking the license
email = 'contact@cloudspectator.com'
key = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'

geekbench_install_dir = 'C:\Program Files'
sqlio_install_dir = 'C:\Program Files (x86)'
