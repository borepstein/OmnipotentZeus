# TESTS TO RUN
# CONFIGURATION INFORMATION

from datetime import datetime

project_id = 'c-edgehosting-20150827'
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

textnotifications = 'n'

# GEEKBENCH LICENSE
# Email and Key for unlocking the license
email = 'contact@cloudspectator.com'
key = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'
