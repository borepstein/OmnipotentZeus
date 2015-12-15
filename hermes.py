from projects.test import *
from datetime import datetime
import json
import os
import subprocess as sub
import smtplib as smtp
import multiprocessing
import zipfile
from time import sleep, time
from collections import OrderedDict as od
from prometheus import Base, Olympus
from prometheus import Ignition
from sqlalchemy.orm import sessionmaker
from random import randint
from psutil import virtual_memory

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
# Download executable files for running tests
if operating_system == 'windows':
    if system_tests == 'y':  # Install Geekbench if to be tested
        if not os.path.isfile(geekbench_install_dir + '\Geekbench 3\geekbench_x86_64.exe'):
            os.system('wget --no-check-certificate https://s3.amazonaws.com/internal-downloads/\
                Geekbench-3.3.2-WindowsSetup.exe')
            sub.call([geekbench_install_dir + '\Geekbench 3\geekbench_x86_64', '-r', email, key])
            sub.call(['Geekbench-3.3.2-WindowsSetup.exe'], shell=True)
        sub.call([geekbench_install_dir + '\Geekbench 3\geekbench_x86_64', '-r', email, key])
    if disk_rand == 'y' or disk_seq == 'y':  # Install fio for disk testing if to be tested
        if not os.path.isfile(fio_install_dir + '\/fio\/fio.exe'):
            os.system('wget http://www.bluestop.org/fio/releases/fio-2.2.10-x86.msi')
            sub.call(['fio-2.2.10-x86.msi'], shell=True)
    if internal_net_tests == 'y':  # Install iperf for network testing if to be tested
        if not os.path.isfile('iperf3.exe'):
            os.system('wget --no-check-certificate https://iperf.fr/download/iperf_3.0/iperf-3.0.11-win64.zip')
            with zipfile.ZipFile('iperf-3.0.11-win64.zip', "r") as z:
                z.extractall()
            os.remove('iperf-3.0.11-win64.zip')
    if iozone == 'y':  # Install iozone if to be tested
        if not os.path.isfile('IozoneSetup.exe'):
            os.system("wget http://www.iozone.org/src/current/IozoneSetup.exe")
        sub.call(['IozoneSetup.exe'], shell=True)

if disk_rand == 'y' or disk_seq == 'y':
    fio_rand_rw = '--rw=randrw'  # randread for random read, randwrite for random write, and randrw for both operations
    fio_seq_rw = '--rw=rw'  # read for sequential read, write for sequential write, and rw for both operations
    disk_options = [fio_rand_rw, fio_seq_rw]

    fio_blocksize = '--bs=' + blocksize + 'k'
    fio_filesize = '--size=' + filesize + "M"
    fio_numjobs = '--numjobs=' + numjobs
    fio_runtime = '--runtime=' + runtime
    fio_json_file = 'fio.json'
    fio_filename = '--name=fio_disk'

    if async_io == 'y':
        fio_async_engine = '--ioengine=windowsaio'

    if direct_io == 'y':
        fio_direct_val = "Direct"
        fio_direct = '--direct=1'
    else:
        fio_direct_val = "Cached"
        fio_direct = '--direct=0'

if iozone == 'y':
    iozone_blocksize = blocksize + 'k'
    iozone_filesize = filesize + 'm'
    iozone_numjobs = numjobs

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

spider_hatchlings = int(numjobs) + 1

# Fetching CPU Amount
vcpu_input = multiprocessing.cpu_count()

# Fetching RAM Amount
mem = virtual_memory()
ram_input = "%.2f" % (float(mem.total) / 1024.0 / 1024.0 / 1024.0)

# Collect information on the provider and VM environment
provider_input = raw_input(
    "Please enter the provider's name (Edge, Netelligent, Rackspace, AWS, SunGard, Peak10, Dimension Data or Azure): ")
provider_input = provider_input.lower()
while True:
    if provider_input == 'edge':
        provider_region = 'N/A'
        break
    elif provider_input == 'netelligent':
        provider_region = 'STL'
        break
    elif provider_input == 'rackspace':
        provider_region = 'DFW'
        break
    elif provider_input == 'aws':
        provider_region = 'us-east'
        break
    elif provider_input == 'azure':
        provider_region = 'us-central'
        break
    elif provider_input == 'sungard':
        provider_region = 'N/A'
        break
    elif provider_input == 'Peak10':
        provider_region = 'N/A'
        break
    elif provider_input == 'dimensiondata':
        provider_region = 'N/A'
        break
    else:
        provider_input = raw_input(
            "Please enter the provider's name (No spaces; e.g., 'Digital Ocean' should be 'digitalocean'): ")
        provider_input = provider_input.lower()

vm_input = raw_input("Please enter the VM name (if no VM name, just say vCPU/RAM in GB (e.g., 2vCPU/4GB): ")
vm_input = vm_input.lower()
vmcount_input = '0'
local_input = raw_input("Local Disk (in GB). Put 0 if none: ")
block_input = raw_input("Block Disk (in GB). Put 0 if none: ")

startdate_input = datetime.now().strftime('%Y%m%d-%H%M')
# Generate a random number to add to the unique ID for this provider and VM combination in the test cycle
random_uid = randint(0, 1000000)
generated_uid = provider_input + vm_input + startdate_input + str(random_uid)

if internal_net_tests == 'y':
    internal_net_ip = raw_input('Please enter the IP address of the server you are trying to connect to: ')

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
        geekbench_output = 'gb.json'

        processor_info = ''
        while True:
            try:
                os.system("start gb_listener.bat")
                sub.call([geekbench_install_dir + '\Geekbench 3\geekbench_x86_64.exe',
                          '--no-upload', '--export-json', geekbench_output], shell=True)

                # Parse variables from Geekbench result
                geekbench_file_handler = open(geekbench_output)
                data = json.load(geekbench_file_handler)
                processor_info = str(data['metrics'][6]['value'])
                if processor_info != '':
                    os.system('taskkill /f /fi "WINDOWTITLE eq C:\Windows\system32\cmd.exe - gb_listener.bat" /fi \
                        "IMAGENAME eq cmd.exe"')
                    os.system('taskkill /f /fi "WINDOWTITLE eq C:\Windows\system32\cmd.exe - gb_listener.bat" /fi \
                        "IMAGENAME eq timeout.exe"')
                    break
            except:
                continue

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

        geekbench_file_handler.close()
        os.remove(geekbench_output)
        print "Completed system tests"

    def fio_exception_handler(fio_command):
        while True:
            try:
                os.system("start fio_listener.bat")
                sub.call(fio_command, stdout=open(fio_json_file, "w"))

                # Parse variables from Geekbench result
                with open(fio_json_file) as fio_results:
                    fio_data = json.load(fio_results)

                iops_read_rand = str(fio_data['jobs'][0]['read']['iops'])
                if iops_read_rand != '':
                    os.system('taskkill /f /fi "WINDOWTITLE eq C:\Windows\system32\cmd.exe - fio_listener.bat" /fi \
                        "IMAGENAME eq cmd.exe"')
                    os.system(
                        'taskkill /f /fi "WINDOWTITLE eq C:\Windows\system32\cmd.exe - fio_listener.bat" /fi \
                        "IMAGENAME eq timeout.exe"')
                    break
            except:
                continue
        return fio_data

    if disk_rand == 'y':

        fio_command = [fio_install_dir + '\/fio\/fio.exe', '--thread', '--group_reporting', '--output-format=json',
                       fio_filename, fio_runtime, disk_options[0], fio_blocksize, fio_direct, fio_filesize, fio_numjobs]
        fio_data = fio_exception_handler(fio_command)

        runtime_read_rand = str(fio_data['jobs'][0]['read']['runtime'])
        runtime_write_rand = str(fio_data['jobs'][0]['write']['runtime'])
        io_read_rand = str(fio_data['jobs'][0]['read']['io_bytes'])
        io_write_rand = str(fio_data['jobs'][0]['write']['io_bytes'])
        iops_read_rand = str(fio_data['jobs'][0]['read']['iops'])
        iops_write_rand = str(fio_data['jobs'][0]['write']['iops'])
        bw_read_rand = str(fio_data['jobs'][0]['read']['bw'])
        bw_write_rand = str(fio_data['jobs'][0]['write']['bw'])

        fio_disk_dir = os.path.dirname(os.path.abspath(__file__))
        for file_name in os.listdir(fio_disk_dir):
            if file_name.startswith('fio_disk'):
                os.remove(os.path.join(fio_disk_dir, file_name))
        os.remove(fio_json_file)

        if async_io == 'y':

            fio_command = [fio_install_dir + '\/fio\/fio.exe', '--thread', '--group_reporting', '--output-format=json',
                           '--iodepth=32', fio_filename, fio_runtime, fio_async_engine, disk_options[0],
                           fio_blocksize, fio_direct, fio_filesize, fio_numjobs]

            fio_data = fio_exception_handler(fio_command)

            runtime_read_rand_async = str(fio_data['jobs'][0]['read']['runtime'])
            runtime_write_rand_async = str(fio_data['jobs'][0]['write']['runtime'])
            io_read_rand_async = str(fio_data['jobs'][0]['read']['io_bytes'])
            io_write_rand_async = str(fio_data['jobs'][0]['write']['io_bytes'])
            iops_read_rand_async = str(fio_data['jobs'][0]['read']['iops'])
            iops_write_rand_async = str(fio_data['jobs'][0]['write']['iops'])
            bw_read_rand_async = str(fio_data['jobs'][0]['read']['bw'])
            bw_write_rand_async = str(fio_data['jobs'][0]['write']['bw'])

            fio_disk_dir = os.path.dirname(os.path.abspath(__file__))
            for file_name in os.listdir(fio_disk_dir):
                if file_name.startswith('fio_disk'):
                    os.remove(os.path.join(fio_disk_dir, file_name))
            os.remove(fio_json_file)

    if disk_seq == 'y':

        fio_command = [fio_install_dir + '\/fio\/fio.exe', '--thread', '--group_reporting', '--output-format=json',
                       fio_filename, fio_runtime, disk_options[1], fio_blocksize, fio_direct, fio_filesize, fio_numjobs]
        fio_data = fio_exception_handler(fio_command)

        runtime_read_seq = str(fio_data['jobs'][0]['read']['runtime'])
        runtime_write_seq = str(fio_data['jobs'][0]['write']['runtime'])
        io_read_seq = str(fio_data['jobs'][0]['read']['io_bytes'])
        io_write_seq = str(fio_data['jobs'][0]['write']['io_bytes'])
        iops_read_seq = str(fio_data['jobs'][0]['read']['iops'])
        iops_write_seq = str(fio_data['jobs'][0]['write']['iops'])
        bw_read_seq = str(fio_data['jobs'][0]['read']['bw'])
        bw_write_seq = str(fio_data['jobs'][0]['write']['bw'])

        fio_disk_dir = os.path.dirname(os.path.abspath(__file__))
        for file_name in os.listdir(fio_disk_dir):
            if file_name.startswith('fio_disk'):
                os.remove(os.path.join(fio_disk_dir, file_name))
        os.remove(fio_json_file)

        if async_io == 'y':

            fio_command = [fio_install_dir + '\/fio\/fio.exe', '--thread', '--group_reporting', '--output-format=json',
                           '--iodepth=32', fio_filename, fio_runtime, fio_async_engine, disk_options[1],
                           fio_blocksize, fio_direct, fio_filesize, fio_numjobs]

            fio_data = fio_exception_handler(fio_command)

            runtime_read_seq_async = str(fio_data['jobs'][0]['read']['runtime'])
            runtime_write_seq_async = str(fio_data['jobs'][0]['write']['runtime'])
            io_read_seq_async = str(fio_data['jobs'][0]['read']['io_bytes'])
            io_write_seq_async = str(fio_data['jobs'][0]['write']['io_bytes'])
            iops_read_seq_async = str(fio_data['jobs'][0]['read']['iops'])
            iops_write_seq_async = str(fio_data['jobs'][0]['write']['iops'])
            bw_read_seq_async = str(fio_data['jobs'][0]['read']['bw'])
            bw_write_seq_async = str(fio_data['jobs'][0]['write']['bw'])

            fio_disk_dir = os.path.dirname(os.path.abspath(__file__))
            for file_name in os.listdir(fio_disk_dir):
                if file_name.startswith('fio_disk'):
                    os.remove(os.path.join(fio_disk_dir, file_name))
            os.remove(fio_json_file)

        print "Completed disk tests"

    if internal_net_tests == 'y':

        # Run iperf test
        iperf_output = 'iperf_results.json'
        sub.call(['iperf3.exe', '-J', '-c', internal_net_ip], stdout=open(iperf_output, "w"))

        # Parse variables from iperf result
        with open(iperf_output) as iperf_results:
            data = json.load(iperf_results)

            sender_transfer_mb = float(data["end"]["sum_sent"]["bytes"]) / (1024 * 1024)
            sender_bandwidth_mbps = float(data["end"]["sum_sent"]["bits_per_second"]) / 1000000
            receiver_transfer_mb = float(data["end"]["sum_received"]["bytes"]) / (1024 * 1024)
            receiver_bandwidth_mbps = float(data["end"]["sum_received"]["bits_per_second"]) / 1000000

        os.remove(iperf_output)
        print "Completed internal network tests"

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

    if iozone == 'y':

        # Sequential Write
        iozone_results = 'iozone_seq_write_results.txt'
        if direct_io == 'y':
            sub.call([iozone_install_dir + '\/iozone.exe', '-I', '-t', iozone_numjobs, '-O', '-r',
                      iozone_blocksize, '-s', iozone_filesize, '-w', '-i', '0'], stdout=open(iozone_results, "w"))
        else:
            sub.call([iozone_install_dir + '\/iozone.exe', '-t', iozone_numjobs, '-O', '-r',
                      iozone_blocksize, '-s', iozone_filesize, '-w', '-i', '0'], stdout=open(iozone_results, "w"))

        target_var = "initial writers"
        iozone_seq_writers = iozone_result_parser(iozone_results, target_var)
        target_var = "rewriters"
        iozone_seq_rewriters = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        # Sequential Read
        iozone_results = 'iozone_seq_read_results.txt'
        if direct_io == 'y':
            sub.call([iozone_install_dir + '\/iozone.exe', '-I', '-t', iozone_numjobs, '-O', '-r',
                      iozone_blocksize, '-s', iozone_filesize, '-w', '-i', '1'], stdout=open(iozone_results, "w"))
        else:
            sub.call([iozone_install_dir + '\/iozone.exe', '-t', iozone_numjobs, '-O', '-r',
                      iozone_blocksize, '-s', iozone_filesize, '-w', '-i', '1'], stdout=open(iozone_results, "w"))

        target_var = "readers"
        iozone_seq_readers = iozone_result_parser(iozone_results, target_var)
        target_var = "re-readers"
        iozone_seq_rereaders = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        # Random Read / Write
        iozone_results = 'iozone_rand_results.txt'
        if direct_io == 'y':
            sub.call([iozone_install_dir + '\/iozone.exe', '-I', '-t', iozone_numjobs, '-O', '-r',
                      iozone_blocksize, '-s', iozone_filesize, '-w', '-i', '2'], stdout=open(iozone_results, "w"))
        else:
            sub.call([iozone_install_dir + '\/iozone.exe', '-t', iozone_numjobs, '-O', '-r',
                      iozone_blocksize, '-s', iozone_filesize, '-w', '-i', '2'], stdout=open(iozone_results, "w"))
        target_var = "random readers"
        iozone_random_readers = iozone_result_parser(iozone_results, target_var)
        target_var = "random writers"
        iozone_random_writers = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        iozone_dummy_exterminator()
        print "completed iozone tests"

    def sysbench_command_generator(sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs,
                                   sysbench_io_mode, sysbench_test_mode, sysbench_runtime, sysbench_results):

        sysbench_command = 'sysbench.exe %s --test=fileio --file-total-size=%s --file-block-size=%s \
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
        os.system('sysbench.exe --test=fileio --file-total-size=%s --file-num=%s cleanup' %
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
        os.system('sysbench.exe --test=fileio --file-total-size=%s --file-num=%s cleanup' %
                  (sysbench_filesize, sysbench_numjobs))

        print "completed sysbench tests"

    # ====================GLOBAL TRANSMITTING==================== #
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
        block=block_input)
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
            Olympus.sender_transfer_mb: sender_transfer_mb,
            Olympus.sender_bandwidth_mbps: sender_bandwidth_mbps,
            Olympus.receiver_transfer_mb: receiver_transfer_mb,
            Olympus.receiver_bandwidth_mbps: receiver_bandwidth_mbps
        })
        session.commit()
        print "Finished transferring internal network test results"

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

# Send text notification
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
