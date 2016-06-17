from projects.test import *
from datetime import datetime
import json
import os
import csv
import subprocess as sub
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
    if geekbench == 'y':
        if not os.path.isfile(geekbench_install_dir + '\Geekbench 3\geekbench_x86_64.exe'):
            os.system('wget --no-check-certificate https://s3.amazonaws.com/internal-downloads/\
                Geekbench-3.3.2-WindowsSetup.exe')
            sub.call(['Geekbench-3.3.2-WindowsSetup.exe'], shell=True)
        sub.call([geekbench_install_dir + '\Geekbench 3\geekbench_x86_64', '-r', email, key])
    if fio == 'y':
        if not os.path.isfile(fio_install_dir + '\/fio\/fio.exe'):
            os.system('wget http://bluestop.org/files/fio/releases/fio-2.11-x64.msi')
            sub.call(['fio-2.11-x64.msi'], shell=True)
    if iperf == 'y':
        if not os.path.isfile('iperf3.exe'):
            os.system('wget --no-check-certificate https://iperf.fr/download/windows/iperf-3.0.11-win64.zip')
            with zipfile.ZipFile('iperf-3.0.11-win64.zip', "r") as z:
                z.extractall()
            os.remove('iperf-3.0.11-win64.zip')
    if iozone == 'y':
        if not os.path.isfile('IozoneSetup.exe'):
            os.system("wget http://www.iozone.org/src/current/IozoneSetup.exe")
        sub.call(['IozoneSetup.exe'], shell=True)
    if passmark == 'y':
        if not os.path.isfile('petst.exe'):
            os.system("wget http://downloads.passmark.com/ftp/petst.exe")
        sub.call(['petst.exe'], shell=True)

if fio == 'y':
    fio_rand_rw = '--rw=randrw'  # randread for random read, randwrite for random write, and randrw for both operations
    fio_seq_rw = '--rw=rw'  # read for sequential read, write for sequential write, and rw for both operations

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
    "Please enter the provider's name (Edge, Netelligent, Rackspace, AWS, Azure, SunGard, Peak10 or Dimension Data): ")
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
    elif provider_input == 'peak10':
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

if iperf == 'y':
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

    if geekbench == 'y':
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

    if passmark == 'y':
        passmark_results = 'passmark_results.csv'
        passmark_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'passmark.pts')

        sub.call([passmark_install_dir + '\PerformanceTest\PerformanceTest64.exe', '/DontGatherGraphics',
                  '/s', passmark_script, '/i', '/ac', passmark_results], shell=True)

        with open(passmark_results, 'rb') as f:
            csv_handler = csv.reader(f)
            for row in csv_handler:
                if "This Computer" in row:
                    cpu_integer_math = row[1]
                    cpu_floating_math = row[2]
                    cpu_prime_numbers = row[3]
                    cpu_extended_instr = row[4]
                    cpu_compression = row[5]
                    cpu_encryption = row[6]
                    cpu_physics = row[7]
                    cpu_sorting = row[8]
                    cpu_single_threaded = row[9]
                    g2d_simple_vectors = row[10]
                    g2d_complex_vectors = row[11]
                    g2d_fonts_text = row[12]
                    g2d_windows_interface = row[13]
                    g2d_image_filters = row[14]
                    g2d_image_rendering = row[15]
                    g3d_direct_2d = row[16]
                    g3d_direct_x9_simple = row[17]
                    g3d_direct_x9_complex = row[18]
                    g3d_direct_x10 = row[19]
                    g3d_direct_x11 = row[20]
                    g3d_direct_compute = row[21]
                    mem_db_operations = row[22]
                    mem_read_cached = row[23]
                    mem_read_uncached = row[24]
                    mem_write = row[25]
                    mem_available_ram = row[26]
                    mem_latency = row[27]
                    mem_threaded = row[28]
                    disk_seq_read = row[29]
                    disk_seq_write = row[30]
                    disk_ran_seq_rw = row[31]
                    cd_dvd_read = row[32]
                    cpu_mark = row[33]
                    two_d_graphics_mark = row[34]
                    mem_mark = row[35]
                    disk_mark = row[36]
                    three_d_graphics_mark = row[37]
                    passmark_rating = row[38]
                    break

        os.remove(passmark_results)
        print "Completed passmark tests"

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

    if fio == 'y':

        # Random Disk Tests
        fio_command = [fio_install_dir + '\/fio\/fio.exe', '--thread', '--group_reporting', '--output-format=json',
                       fio_filename, fio_runtime, fio_rand_rw, fio_blocksize, fio_direct, fio_filesize, fio_numjobs]
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
                           '--iodepth=32', fio_filename, fio_runtime, fio_async_engine, fio_rand_rw,
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

        # Sequential Disk Tests
        fio_command = [fio_install_dir + '\/fio\/fio.exe', '--thread', '--group_reporting', '--output-format=json',
                       fio_filename, fio_runtime, fio_seq_rw, fio_blocksize, fio_direct, fio_filesize, fio_numjobs]
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
                           '--iodepth=32', fio_filename, fio_runtime, fio_async_engine, fio_seq_rw,
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

        print "Completed fio tests"

    if iperf == 'y':

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

    if geekbench == 'y':

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

    if fio == 'y':

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

    if iperf == 'y':

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

    if passmark == 'y':
        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.pm_cpu_integer_math: cpu_integer_math,
            Olympus.pm_cpu_floating_math: cpu_floating_math,
            Olympus.pm_cpu_prime_numbers: cpu_prime_numbers,
            Olympus.pm_cpu_extended_instr: cpu_extended_instr,
            Olympus.pm_cpu_compression: cpu_compression,
            Olympus.pm_cpu_encryption: cpu_encryption,
            Olympus.pm_cpu_physics: cpu_physics,
            Olympus.pm_cpu_sorting: cpu_sorting,
            Olympus.pm_cpu_single_threaded: cpu_single_threaded,
            Olympus.pm_g2d_simple_vectors: g2d_simple_vectors,
            Olympus.pm_g2d_complex_vectors: g2d_complex_vectors,
            Olympus.pm_g2d_fonts_text: g2d_fonts_text,
            Olympus.pm_g2d_windows_interface: g2d_windows_interface,
            Olympus.pm_g2d_image_filters: g2d_image_filters,
            Olympus.pm_g2d_image_rendering: g2d_image_rendering,
            Olympus.pm_g3d_direct_2d: g3d_direct_2d,
            Olympus.pm_g3d_direct_x9_simple: g3d_direct_x9_simple,
            Olympus.pm_g3d_direct_x9_complex: g3d_direct_x9_complex,
            Olympus.pm_g3d_direct_x10: g3d_direct_x10,
            Olympus.pm_g3d_direct_x11: g3d_direct_x11,
            Olympus.pm_g3d_direct_compute: g3d_direct_compute,
            Olympus.pm_mem_db_operations: mem_db_operations,
            Olympus.pm_mem_read_cached: mem_read_cached,
            Olympus.pm_mem_read_uncached: mem_read_uncached,
            Olympus.pm_mem_write: mem_write,
            Olympus.pm_mem_available_ram: mem_available_ram,
            Olympus.pm_mem_latency: mem_latency,
            Olympus.pm_mem_threaded: mem_threaded,
            Olympus.pm_disk_seq_read: disk_seq_read,
            Olympus.pm_disk_seq_write: disk_seq_write,
            Olympus.pm_disk_ran_seq_rw: disk_ran_seq_rw,
            Olympus.pm_cd_dvd_read: cd_dvd_read,
            Olympus.pm_cpu_mark: cpu_mark,
            Olympus.pm_two_d_graphics_mark: two_d_graphics_mark,
            Olympus.pm_mem_mark: mem_mark,
            Olympus.pm_disk_mark: disk_mark,
            Olympus.pm_three_d_graphics_mark: three_d_graphics_mark,
            Olympus.pm_passmark_rating: passmark_rating
        })

        session.commit()
        print "Finished transferring passmark results"

    print "\n\n"
    print "All tests are successfully completed and the results are transferred to our database"
    print "\n\n"

    iterator = iterator + 1
    # Any delay before the next round is executed
    sleep(sleeptime)
