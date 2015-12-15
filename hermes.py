from projects.test import *
from datetime import datetime
import json
import os
import csv
import subprocess as sub
import smtplib as smtp
from time import sleep, time
from collections import OrderedDict as od
from prometheus import Base, Olympus
from prometheus import Ignition
from sqlalchemy.orm import sessionmaker
from random import randint

# Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
DBSession = sessionmaker(bind=Ignition)
session = DBSession()

# ==================== GLOBAL INTRODUCTION ==================== #
os.system('clear')
print "|------------------------|"
print "|    Project Olympus     |"
print "|         v1.5           |"
print "|------------------------|"
print ""
print "Project Olympus is designed to be a testbed for measuring virtual machine performance in a scalable, \
cloud environment. The design of Olympus is its flexibility in continuous testing over time, rather than \
spot testing, which is an archaic method that cannot apply to highly variable environments with multiple \
(many of which are possibly uncontrolled) variables.\n\n"

# ==================== GLOBAL INSTALLER ==================== #
if operating_system == 'centos' or operating_system == 'redhat':
    if disk_rand == 'y' or disk_seq == 'y':  # Install fio for disk testing if to be tested
        os.system('wget http://pkgs.repoforge.org/fio/fio-2.1.10-1.el6.rf.x86_64.rpm')
        os.system('rpm -iv fio-2.1.10-1.el6.rf.x86_64.rpm')
    if internal_net_tests == 'y':  # Install iperf for network testing if to be tested
        os.system('yum install iperf -y')
    if system_tests == 'y':  # Install Geekbench - Download & Unpackage if to be tested
        os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz")
        os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
        os.chdir('dist/Geekbench-3.1.2-Linux')
        sub.call(['./geekbench_x86_64', '-r', email, key])
    if apachebench == 'y':  # Install ApacheBench if to be tested
        os.system('yum install httpd-tools')
    if iozone == 'y':  # Install iozone if to be tested
        os.system("wget http://www.iozone.org/src/current/iozone-3-338.i386.rpm")
        os.system("rpm -ivh iozone-3-338.i386.rpm")
    if sysbench == 'y':
        os.system('yum -y install sysbench')

if operating_system == 'ubuntu' or operating_system == 'debian':
    if disk_rand == 'y' or disk_seq == 'y':  # Install fio for disk testing if to be tested
        os.system('apt-get install fio --yes')
    if internal_net_tests == 'y':  # Install iperf for network testing if to be tested
        os.system('apt-get install iperf')
    if system_tests == 'y':  # Install Geekbench - Download & Unpackage if to be tested
        # os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz")
        # os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
        os.chdir('dist/Geekbench-3.1.2-Linux')
        sub.call(['./geekbench_x86_64', '-r', email, key])
    if apachebench == 'y':  # Install ApacheBench if to be tested
        os.system('apt-get install apache2-utils')
    if iozone == 'y':  # Install iozone if to be tested
        os.system('apt-get install iozone3')
    if sysbench == 'y':
        os.system('sudo apt-get install sysbench')

if disk_rand == 'y' or disk_seq == 'y':
    fio_rand_rw = '-rw=randrw'  # randread for random read, randwrite for random write, and randrw to do both operations
    fio_seq_rw = '-rw=rw'  # read for sequential read, write for sequential write, and rw to do both operations
    disk_options = [fio_seq_rw, fio_rand_rw]

    fio_blocksize = '-bs=' + blocksize + 'k'
    fio_filesize = '-size=' + filesize + "M"
    spider_hatchlings = int(numjobs) + 1
    fio_numjobs = '-numjobs=' + numjobs
    fio_runtime = '-runtime=' + runtime
    fio_json_file = 'fio.json'
    fio_filename = '-name=spider_eggs'
    if direct_io == 'y':
        fio_direct_val = "Direct"
        fio_direct = '-direct=1'
    else:
        fio_direct_val = "Cached"
        fio_direct = '-direct=0'

if iozone == 'y':
    iozone_blocksize = blocksize + 'k'
    iozone_filesize = filesize + 'm'
    iozone_numjobs = numjobs
    if direct_io == 'y':
        iozone_direct = '-I'
    else:
        iozone_direct = ''

if sysbench == 'y':
    sysbench_blocksize = blocksize + 'K'
    sysbench_filesize = str(int(filesize) * int(numjobs)) + 'M'
    sysbench_numjobs = numjobs
    sysbench_runtime = runtime

    if async_io == 'y':
        sysbench_io_mode = 'async'
    else:
        sysbench_io_mode = 'sync'

    if direct_io == 'y':
        sysbench_direct = '--file-extra-flags=direct'
    else:
        sysbench_direct = ''

processor_info = ""
# Getting CPU Amount
v1 = sub.Popen(['cat', '/proc/cpuinfo'], stdout=sub.PIPE)
v2 = sub.Popen(['grep', 'processor'], stdin=v1.stdout, stdout=sub.PIPE)
v3 = sub.Popen(['wc', '-l'], stdin=v2.stdout, stdout=sub.PIPE)
vcpu_input = v3.communicate()[0]

# RAM Amount
r1 = sub.Popen(['cat', '/proc/meminfo'], stdout=sub.PIPE)
r2 = sub.Popen(['grep', 'MemTotal'], stdin=r1.stdout, stdout=sub.PIPE)
memoutput = r2.communicate()[0]
memoutput_list = memoutput.split(' ')
for x in memoutput_list:
    if x.isalnum():  # Converting from bytes to GB
        mem_count = int(x)
        mem_count = (mem_count / 1024.0 / 1024.0)
        ram_input = "%.2f" % mem_count

# Collect information on the provider and VM environment
provider_input = raw_input("\nPlease enter the provider's name: ")
provider_input = provider_input.lower()
provider_region = "N/A"

vm_input = raw_input("Please enter the VM name (if no VM name, just say vCPU/RAM in GB (e.g., 2vCPU/4GB): ")
vm_input = vm_input.lower()
vmcount_input = raw_input(
    "Which VM copy is this? (i.e., you need to test 3 of each machine for 24 hours. Is this machine 1, 2, or 3?) ")
local_input = "0"
block_input = "0"

startdate_input = datetime.now().strftime('%Y%m%d-%H%M')
# Generate a random number to add to the unique ID for this provider and VM combination in the test cycle
random_uid = randint(0, 1000000)
generated_uid = provider_input + vm_input + startdate_input + str(random_uid)

if disk_rand == 'y':
    fio_rw = "Yes"

if disk_seq == 'y':
    fio_seq = "Yes"

if internal_net_tests == 'y':
    internal_net_ip = raw_input('Please enter the IP address of the server you are trying to connect to: ')
    internal_net_csv = "C"

# ==================== GLOBAL TESTING ==================== #
iterator = 1
start = time()
for x in range(iterations):
    stop = time() - start
    if stop >= duration:
        break

    print "\n#######################################################\n"
    print "Iteration: " + str(iterator)
    print "\n#######################################################\n"

    iteration_start_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    if system_tests == 'y':
        # Run Geekbench
        sub.call(['./geekbench_x86_64', '--no-upload', '--export-json', 'gb.json'])

        geekbench_json = open('gb.json')
        data = json.load(geekbench_json)
        if iterator == 1:
            processor_info = str(data['metrics'][6]['value'])

        # Parse results
        y = 0
        scores = {}
        for x in range(0, 13, 1):
            z = str(data['sections'][0]['workloads'][y]['name'])
            scores[z] = str(data['sections'][0]['workloads'][y]['results'][1]['rate_string'])
            y = y + 1
        y = 0
        for x in range(0, 10, 1):
            z = str(data['sections'][1]['workloads'][y]['name'])
            scores[z] = str(data['sections'][1]['workloads'][y]['results'][1]['rate_string'])
            y = y + 1
        y = 0
        for x in range(0, 4, 1):
            z = str(data['sections'][2]['workloads'][y]['name'])
            scores[z] = str(data['sections'][2]['workloads'][y]['results'][1]['rate_string'])
            y = y + 1
        y = 0
        for x in range(0, 3, 1):
            z = str(data['sections'][y]['name']) + " Multicore"
            scores[z] = str(data['sections'][y]['multicore_score'])
            y = y + 1
        y = 0
        for x in range(0, 3, 1):
            z = str(data['sections'][y]['name']) + " Singlecore"
            scores[z] = str(data['sections'][y]['score'])
            y = y + 1
        y = 0
        for x in range(0, 1):
            z = "Total"
            scores[z] = str(data['multicore_score'])
            y = y + 1
        for x in range(0, 1):
            z = "Total Single"
            scores[z] = str(data['multicore_score'])
            y = y + 1
        for x in range(0, 1):
            z = "Runtime"
            scores[z] = str(data['runtime'])

        scores = od(scores)
        y = 0
        values = {}
        for key, val in scores.items():
            if "GB/sec" in val or "Gflops" in val:
                values[key] = float(val[:-7]) * 1024
            elif "MB/sec" in val or "Mflops" in val:
                values[key] = float(val[:-7])
            elif "Gpixels/sec" in val:
                values[key] = float(val[:-12]) * 1024
            elif "Mpixels/sec" in val:
                values[key] = float(val[:-12])
            elif "Gpairs/sec" in val:
                values[key] = float(val[:-11]) * 1024
            elif "Mpairs/sec" in val:
                values[key] = float(val[:-11])
            else:
                values[key] = val
            y = y + 1
        values = od(values)
        print "completed geekbench test"

    def fio_command_generator(option):
        global fio_command
        fio_command = ['fio', option, fio_filename, fio_blocksize, fio_filesize, fio_numjobs, fio_runtime, fio_direct,
                       '-time_based', '--output-format=json', '--output=fio.json', '-time_based', '-group_reporting',
                       '-exitall']
        return fio_command

    def fio_async_command_generator(option):
        global fio_command
        fio_command = ['fio', option, fio_filename, "-bs=128k", "-size=128M", "-numjobs=8", fio_runtime, fio_direct,
                       '-iodepth=32', '-ioengine=libaio', '-time_based', '--output-format=json', '--output=fio.json',
                       '-time_based', '-group_reporting', '-exitall']
        return fio_command

    def spider_egg_exterminator():
        fio_json.close()
        os.remove(fio_json_file)
        for baby_spiders in range(0, spider_hatchlings):
            spideregg_file = "spider_eggs." + str(baby_spiders) + ".0"
            try:
                os.remove(spideregg_file)
            except:
                print 'no file'

    if disk_rand == 'y':
        sub.call(fio_command_generator(disk_options[0]))
        fio_json = open(fio_json_file)
        fio_data = json.load(fio_json)

        runtime_read_rand = str(fio_data['jobs'][0]['read']['runtime'])
        runtime_write_rand = str(fio_data['jobs'][0]['write']['runtime'])
        ops_read_rand = str(fio_data['disk_util'][0]['read_ios'])
        ops_write_rand = str(fio_data['disk_util'][0]['write_ios'])
        io_read_rand = str(fio_data['jobs'][0]['read']['io_bytes'])
        io_write_rand = str(fio_data['jobs'][0]['write']['io_bytes'])
        iops_read_rand = str(fio_data['jobs'][0]['read']['iops'])
        iops_write_rand = str(fio_data['jobs'][0]['write']['iops'])
        bw_read_rand = str(fio_data['jobs'][0]['read']['bw'])
        bw_write_rand = str(fio_data['jobs'][0]['write']['bw'])
        ticks_read_rand = str(fio_data['disk_util'][0]['read_ticks'])
        ticks_write_rand = str(fio_data['disk_util'][0]['write_ticks'])

        spider_egg_exterminator()

        if async_io == 'y':
            sub.call(fio_async_command_generator(disk_options[0]))
            fio_json = open(fio_json_file)
            fio_data = json.load(fio_json)

            runtime_read_rand_async = str(fio_data['jobs'][0]['read']['runtime'])
            runtime_write_rand_async = str(fio_data['jobs'][0]['write']['runtime'])
            ops_read_rand_async = str(fio_data['disk_util'][0]['read_ios'])
            ops_write_rand_async = str(fio_data['disk_util'][0]['write_ios'])
            io_read_rand_async = str(fio_data['jobs'][0]['read']['io_bytes'])
            io_write_rand_async = str(fio_data['jobs'][0]['write']['io_bytes'])
            iops_read_rand_async = str(fio_data['jobs'][0]['read']['iops'])
            iops_write_rand_async = str(fio_data['jobs'][0]['write']['iops'])
            bw_read_rand_async = str(fio_data['jobs'][0]['read']['bw'])
            bw_write_rand_async = str(fio_data['jobs'][0]['write']['bw'])
            ticks_read_rand_async = str(fio_data['disk_util'][0]['read_ticks'])
            ticks_write_rand_async = str(fio_data['disk_util'][0]['write_ticks'])

            spider_egg_exterminator()
        print "completed random disk tests"

    if disk_seq == 'y':
        sub.call(fio_command_generator(disk_options[1]))
        fio_json = open(fio_json_file)
        fio_data = json.load(fio_json)

        runtime_read_seq = str(fio_data['jobs'][0]['read']['runtime'])
        runtime_write_seq = str(fio_data['jobs'][0]['write']['runtime'])
        ops_read_seq = str(fio_data['disk_util'][0]['read_ios'])
        ops_write_seq = str(fio_data['disk_util'][0]['write_ios'])
        io_read_seq = str(fio_data['jobs'][0]['read']['io_bytes'])
        io_write_seq = str(fio_data['jobs'][0]['write']['io_bytes'])
        iops_read_seq = str(fio_data['jobs'][0]['read']['iops'])
        iops_write_seq = str(fio_data['jobs'][0]['write']['iops'])
        bw_read_seq = str(fio_data['jobs'][0]['read']['bw'])
        bw_write_seq = str(fio_data['jobs'][0]['write']['bw'])
        ticks_read_seq = str(fio_data['disk_util'][0]['read_ticks'])
        ticks_write_seq = str(fio_data['disk_util'][0]['write_ticks'])

        spider_egg_exterminator()
        if async_io == 'y':
            sub.call(fio_async_command_generator(disk_options[1]))
            fio_json = open(fio_json_file)
            fio_data = json.load(fio_json)

            runtime_read_seq_async = str(fio_data['jobs'][0]['read']['runtime'])
            runtime_write_seq_async = str(fio_data['jobs'][0]['write']['runtime'])
            ops_read_seq_async = str(fio_data['disk_util'][0]['read_ios'])
            ops_write_seq_async = str(fio_data['disk_util'][0]['write_ios'])
            io_read_seq_async = str(fio_data['jobs'][0]['read']['io_bytes'])
            io_write_seq_async = str(fio_data['jobs'][0]['write']['io_bytes'])
            iops_read_seq_async = str(fio_data['jobs'][0]['read']['iops'])
            iops_write_seq_async = str(fio_data['jobs'][0]['write']['iops'])
            bw_read_seq_async = str(fio_data['jobs'][0]['read']['bw'])
            bw_write_seq_async = str(fio_data['jobs'][0]['write']['bw'])
            ticks_read_seq_async = str(fio_data['disk_util'][0]['read_ticks'])
            ticks_write_seq_async = str(fio_data['disk_util'][0]['write_ticks'])

            spider_egg_exterminator()
        print "completed sequential disk tests"

    if internal_net_tests == 'y':
        internal_net_csv_file = 'iperf_results.csv'
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time,
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            internal_network_data = (int(row[7]) / 1024) / 1024
            internal_network_bandwidth = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)
        print "completed internal network tests"

    if apachebench == 'y':
        ab_results = "ab_results.txt"
        ab_address = ab_hostname
        if ab_port:
            ab_address = ab_address + ":" + ab_port
        if ab_path:
            ab_address = ab_address + ab_path

        sub.call(['ab', '-q', '-n', ab_requests, '-c', ab_concurrency, '-s', ab_timeout,
                  '-e', ab_results, ab_address], stdout=open(ab_results, "w"))
        with open(ab_results) as f:
            lines = f.readlines()
            for l in lines:
                if("Requests per second" in l):
                    requests_per_sec = filter(None, l.split(" "))[3]
                if("Time taken for tests:" in l):
                    time_taken = filter(None, l.split(" "))[4]
                if("50%" in l):
                    percent_50 = filter(None, l.split(" "))[1]
                if("66%" in l):
                    percent_66 = filter(None, l.split(" "))[1]
                if("75%" in l):
                    percent_75 = filter(None, l.split(" "))[1]
                if("80%" in l):
                    percent_80 = filter(None, l.split(" "))[1]
                if("90%" in l):
                    percent_90 = filter(None, l.split(" "))[1]
                if("95%" in l):
                    percent_95 = filter(None, l.split(" "))[1]
                if("98%" in l):
                    percent_98 = filter(None, l.split(" "))[1]
                if("99%" in l):
                    percent_99 = filter(None, l.split(" "))[1]
                if("100%" in l):
                    percent_100 = filter(None, l.split(" "))[1]

        os.remove(ab_results)
        print "completed apachebench tests"

    def iozone_dummy_exterminator():
        for iozone_dummy in range(0, spider_hatchlings - 1):
            iozone_dummy_file = "iozone.DUMMY." + str(iozone_dummy)
            try:
                os.remove(iozone_dummy_file)
            except:
                print 'no file'

    def iozone_result_parser(result_file, target_var):
        with open(result_file) as f:
            lines = f.readlines()
            for l in lines:
                if target_var in l:
                    target_res = l.split("=")
                    target_res = filter(None, target_res[1].split(" "))
                    target_res = target_res[0]
                    return target_res
                    break

    if iozone == 'y':

        # Sequential Write, 64K requests, 32 threads:
        iozone_results = 'iozone_seq_write_results.txt'
        os.system('iozone %s -t %s -O -r %s -s %s -w -i 0 > %s' %
                  (iozone_direct, iozone_numjobs, iozone_blocksize, iozone_filesize, iozone_results))
        target_var = "initial writers"
        iozone_seq_writers = iozone_result_parser(iozone_results, target_var)
        target_var = "rewriters"
        iozone_seq_rewriters = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        # Sequential Read, 64K requests, 32 threads:
        iozone_results = 'iozone_seq_read_results.txt'
        os.system('iozone %s -t %s -M -O -r %s -s %s -w -i 1 > %s' %
                  (iozone_direct, iozone_numjobs, iozone_blocksize, iozone_filesize, iozone_results))
        target_var = "readers"
        iozone_seq_readers = iozone_result_parser(iozone_results, target_var)
        target_var = "re-readers"
        iozone_seq_rereaders = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        # Random Read / Write, 4K requests, 32 threads:
        iozone_results = 'iozone_rand_results.txt'
        os.system('iozone %s -t %s -M -O -r %s -s %s -w -i 2 > %s' %
                  (iozone_direct, iozone_numjobs, iozone_blocksize, iozone_filesize, iozone_results))
        target_var = "random readers"
        iozone_random_readers = iozone_result_parser(iozone_results, target_var)
        target_var = "random writers"
        iozone_random_writers = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        iozone_dummy_exterminator()
        print "completed iozone tests"

    def sysbench_command_generator(sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs,
                                   sysbench_io_mode, sysbench_test_mode, sysbench_runtime, sysbench_results):

        sysbench_command = 'sysbench %s --test=fileio --file-total-size=%s --file-block-size=%s \
        --file-num=%s --num-threads=%s --file-io-mode=%s --file-test-mode=%s --max-time=%s run > %s' % (
            sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_numjobs,
            sysbench_io_mode, sysbench_test_mode, sysbench_runtime, sysbench_results)

        return sysbench_command

    def sysbench_result_parser(sysbench_results, sysbench_test_mode):
        with open(sysbench_results) as f:
            lines = f.readlines()
            target = 'Requests/sec'
            for l in lines:
                if target in l:
                    res = filter(None, l.split(" "))
                    return res[0]
                    break

    if sysbench == 'y':

        sysbench_results = 'sysbench_results.txt'

        sysbench_test_mode = 'seqwr'
        sysbench_command = sysbench_command_generator(
            sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
            sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_seq_write = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)

        sysbench_test_mode = 'seqrd'
        sysbench_command = sysbench_command_generator(
            sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
            sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_seq_read = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)
        os.system('sysbench --test=fileio --file-total-size=%s --file-num=%s cleanup' %
                  (sysbench_filesize, sysbench_numjobs))

        sysbench_test_mode = 'rndwr'
        sysbench_command = sysbench_command_generator(
            sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
            sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_rand_write = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)

        sysbench_test_mode = 'rndrd'
        sysbench_command = sysbench_command_generator(
            sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
            sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_rand_read = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)
        os.system('sysbench --test=fileio --file-total-size=%s --file-num=%s cleanup' %
                  (sysbench_filesize, sysbench_numjobs))

        print "completed sysbench tests"

    if disk_rand == 'n' and disk_seq == 'n':
        fio_rw = "n/a"
        fio_seq = "n/a"
        fio_blocksize = 0
        fio_filesize = 0
        fio_numjobs = 0
        fio_direct_val = 0

# ==================== GLOBAL TRANSMITTING ==================== #
    # Transmit data back to Olympus
    print "\n\n"
    print "Transmitting to Olympus"
    print "\n\n"
    Open_Olympus = Olympus(
        project=project_id,
        uid=generated_uid,
        provider=provider_input,
        region=provider_region,
        startdate=startdate_input,
        iteration=iterator,
        iteration_start_time=iteration_start_time,
        vm=vm_input,
        vmcount=vmcount_input,
        vcpu=vcpu_input,
        ram=ram_input,
        local=local_input,
        block=block_input,
        disk_rand=fio_rw,
        disk_seq=fio_seq,
        disk_blocksize=fio_blocksize,
        disk_filesize=fio_filesize,
        disk_numjobs=fio_numjobs,
        disk_direct=fio_direct_val)
    session.add(Open_Olympus)
    session.commit()
    print "Basic information transfer complete"

    if system_tests == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.processor: processor_info,
            Olympus.runtime: values['Runtime'],
            Olympus.intmulti: values['Integer Multicore'],
            Olympus.floatmulti: values['Floating Point Multicore'],
            Olympus.memmulti: values['Memory Multicore'],
            Olympus.intsingle: values['Integer Singlecore'],
            Olympus.floatsingle: values['Floating Point Singlecore'],
            Olympus.memsingle: values['Memory Singlecore'],
            Olympus.totalmulti: values['Total'],
            Olympus.totalsingle: values['Total Single'],
            Olympus.aes: values['AES'],
            Olympus.twofish: values['Twofish'],
            Olympus.sha1: values['SHA1'],
            Olympus.sha2: values['SHA2'],
            Olympus.bzipcompression: values['BZip2 Compress'],
            Olympus.bzipdecompression: values['BZip2 Decompress'],
            Olympus.jpegcompression: values['JPEG Compress'],
            Olympus.jpegdecompression: values['JPEG Decompress'],
            Olympus.pngcompression: values['PNG Compress'],
            Olympus.pngdecompression: values['PNG Decompress'],
            Olympus.sobel: values['Sobel'],
            Olympus.lua: values['Lua'],
            Olympus.dijkstra: values['Dijkstra'],
            Olympus.blackscholes: values['BlackScholes'],
            Olympus.mandelbrot: values['Mandelbrot'],
            Olympus.sharpenimage: values['Sharpen Filter'],
            Olympus.blurimage: values['Blur Filter'],
            Olympus.sgemm: values['SGEMM'],
            Olympus.dgemm: values['DGEMM'],
            Olympus.sfft: values['SFFT'],
            Olympus.dfft: values['DFFT'],
            Olympus.nbody: values['N-Body'],
            Olympus.raytrace: values['Ray Trace'],
            Olympus.copy: values['Stream Copy'],
            Olympus.scale: values['Stream Scale'],
            Olympus.add: values['Stream Add'],
            Olympus.triad: values['Stream Triad']
        })
        session.commit()
        print "Finished transferring geekbench results"

    if disk_rand == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.iops_read_rand: iops_read_rand,
            Olympus.iops_write_rand: iops_write_rand,
            Olympus.io_read_rand: io_read_rand,
            Olympus.io_write_rand: io_write_rand,
            Olympus.runtime_read_rand: runtime_read_rand,
            Olympus.runtime_write_rand: runtime_write_rand,
            Olympus.bw_read_rand: bw_read_rand,
            Olympus.bw_write_rand: bw_write_rand
        })
        session.commit()

        if async_io == 'y':

            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.iops_read_rand_async: iops_read_rand_async,
                Olympus.iops_write_rand_async: iops_write_rand_async,
                Olympus.io_read_rand_async: io_read_rand_async,
                Olympus.io_write_rand_async: io_write_rand_async,
                Olympus.runtime_read_rand_async: runtime_read_rand_async,
                Olympus.runtime_write_rand_async: runtime_write_rand_async,
                Olympus.bw_read_rand_async: bw_read_rand_async,
                Olympus.bw_write_rand_async: bw_write_rand_async
            })
            session.commit()

        print "Finished transferring disk random results"

    if disk_seq == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.iops_read_seq: iops_read_seq,
            Olympus.iops_write_seq: iops_write_seq,
            Olympus.io_read_seq: io_read_seq,
            Olympus.io_write_seq: io_write_seq,
            Olympus.runtime_read_seq: runtime_read_seq,
            Olympus.runtime_write_seq: runtime_write_seq,
            Olympus.bw_read_seq: bw_read_seq,
            Olympus.bw_write_seq: bw_write_seq
        })
        session.commit()

        if async_io == 'y':
            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.iops_read_seq_async: iops_read_seq_async,
                Olympus.iops_write_seq_async: iops_write_seq_async,
                Olympus.io_read_seq_async: io_read_seq_async,
                Olympus.io_write_seq_async: io_write_seq_async,
                Olympus.runtime_read_seq_async: runtime_read_seq_async,
                Olympus.runtime_write_seq_async: runtime_write_seq_async,
                Olympus.bw_read_seq_async: bw_read_seq_async,
                Olympus.bw_write_seq_async: bw_write_seq_async
            })
            session.commit()

        print "Finished transferring disk sequential results"

    if internal_net_tests == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.internal_network_data: internal_network_data,
            Olympus.internal_network_bandwidth: internal_network_bandwidth
        })
        session.commit()
        print "Finished transferring internal network test results"

    if apachebench == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.hostname: ab_address,
            Olympus.concurrency_level: ab_concurrency,
            Olympus.completed_requests: ab_requests,
            Olympus.time_taken: time_taken,
            Olympus.requests_per_sec: requests_per_sec,
            Olympus.percent_50: percent_50,
            Olympus.percent_66: percent_66,
            Olympus.percent_75: percent_75,
            Olympus.percent_80: percent_80,
            Olympus.percent_90: percent_90,
            Olympus.percent_95: percent_95,
            Olympus.percent_98: percent_98,
            Olympus.percent_99: percent_99,
            Olympus.percent_100: percent_100
        })

        session.commit()
        print "Finished transferring apache bench test results"

    if iozone == 'y':
        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.iozone_seq_writers: iozone_seq_writers,
            Olympus.iozone_seq_rewriters: iozone_seq_rewriters,
            Olympus.iozone_seq_readers: iozone_seq_readers,
            Olympus.iozone_seq_rereaders: iozone_seq_rereaders,
            Olympus.iozone_random_readers: iozone_random_readers,
            Olympus.iozone_random_writers: iozone_random_writers,
        })

        session.commit()
        print "Finished transferring iozone results"

    if sysbench == 'y':
        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.sysbench_seq_write: sysbench_seq_write,
            Olympus.sysbench_seq_read: sysbench_seq_read,
            Olympus.sysbench_rand_write: sysbench_rand_write,
            Olympus.sysbench_rand_read: sysbench_rand_read,
        })

        session.commit()
        print "Finished transferring sysbench results"

    print "\n\n"
    print "All tests are successfully completed and the results are transferred to our database"
    print "\n\n"

    iterator = iterator + 1
    # Any delay before the next round is executed
    sleep(sleeptime)

if textnotifications == 'y':
    try:
        server = smtp.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(smtp_username, smtp_password)
        message = tester_name + ", the testing on your " + provider_input + " VM (" + vm_input + ") is completed."
        FROM = 'Hermestxtnotifications@gmail.com'
        server.sendmail(FROM, TO, message)
        server.close()
        print "Text Sent"
    except:
        print "Not sent"
