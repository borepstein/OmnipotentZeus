from projects.test import *
from datetime import datetime
import json
import os
import csv
import subprocess as sub
from time import sleep, time
from collections import OrderedDict as od
from prometheus import Base, Ignition, Virtualmachine, Processordata, Memorydata, Localdiskdata, Internalnetworkdata
from sqlalchemy.orm import sessionmaker

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

provider_data = {
    1: "aws",
    2: "azure"
}

vm_data = {
    1: "aws",
    2: "azure"
}

os_data = {
    1: "windows",
    2: "linux"
}

cores_data = {
    1: "1",
    2: "2",
    3: "4"
}

# ==================== GLOBAL INSTALLER ==================== #
if fio == 'y':
    os.system('apt-get install fio --yes')
if iperf == 'y':
    os.system('apt-get install iperf')
if geekbench == 'y':
    if not os.path.isfile(geekbench_install_dir + '/geekbench_x86_64'):
        os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz")
        os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
    os.chdir(geekbench_install_dir)
    sub.call(['./geekbench_x86_64', '-r', email, key])

if fio == 'y':
    fio_rand_rw = '-rw=randrw'  # randread for random read, randwrite for random write, and randrw to do both operations
    fio_seq_rw = '-rw=rw'  # read for sequential read, write for sequential write, and rw to do both operations

    fio_blocksize = '-bs=' + blocksize + 'k'
    fio_filesize = '-size=' + filesize + "M"
    spider_hatchlings = int(numjobs) + 1
    fio_numjobs = '-numjobs=' + numjobs
    fio_runtime = '-runtime=' + runtime
    fio_json_file = 'fio.json'
    fio_filename = '-name=spider_eggs'
    if direct_io == 'y':
        fio_direct = '-direct=1'
    else:
        fio_direct = '-direct=0'

# Provider name
provider_name = raw_input("\nPlease enter the provider's name: ")
provider_name = provider_name.lower()

try:
    provider_id = provider_data.keys()[provider_data.values().index(provider_name)]
except ValueError as e:
    print "\nInvalid data for Provider input"
    exit()

provider_location = raw_input("\nPlease enter the provider's location: ")
provider_location = provider_location.lower()

# VM name
vm_name = raw_input("\nPlease enter the VM name: ")
vm_name = vm_name.lower()

try:
    vm_id = vm_data.keys()[vm_data.values().index(vm_name)]
except ValueError as e:
    print "\nInvalid data for VM input"
    exit()

# Operating system
os_name = raw_input("\nPlease enter the Operating System name: ")
os_name = os_name.lower()

try:
    os_id = os_data.keys()[os_data.values().index(os_name)]
except ValueError as e:
    print "\nInvalid data for OS input"
    exit()

if iperf == 'y':
    internal_net_ip = raw_input('\nPlease enter the IP address of the server you are trying to connect to: ')
    internal_net_csv = "C"

processor_info = ""
# Getting CPU Amount
v1 = sub.Popen(['cat', '/proc/cpuinfo'], stdout=sub.PIPE)
v2 = sub.Popen(['grep', 'processor'], stdin=v1.stdout, stdout=sub.PIPE)
v3 = sub.Popen(['wc', '-l'], stdin=v2.stdout, stdout=sub.PIPE)
cores = v3.communicate()[0]

# Cores
try:
    cores_id = cores_data.keys()[cores_data.values().index(cores.strip())]
except ValueError as e:
    print "\nInvalid data for CPU cores"
    exit()

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

startdate_input = datetime.now().strftime('%Y%m%d-%H%M')

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
            scores[z] = str(data['score'])
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
        print "\ncompleted geekbench test"

    def fio_command_generator(option):
        global fio_command
        fio_command = ['fio', option, fio_filename, fio_blocksize, fio_filesize, fio_numjobs, fio_runtime, fio_direct,
                       '-output-format=json', '-output=fio.json', '-time_based', '-group_reporting',
                       '-exitall']
        print "\n"
        print fio_command
        return fio_command

    def fio_async_command_generator(option):
        global fio_command
        fio_command = ['fio', option, fio_filename, fio_blocksize, fio_filesize, fio_numjobs, fio_runtime, fio_direct,
                       '-output-format=json', '-output=fio.json', '-time_based', '-group_reporting',
                       '-iodepth=32', '-ioengine=libaio', '-exitall']
        print "\n"
        print fio_command
        return fio_command

    def spider_egg_exterminator():
        fio_json.close()
        os.remove(fio_json_file)
        for baby_spiders in range(0, spider_hatchlings):
            spideregg_file = "spider_eggs." + str(baby_spiders) + ".0"
            try:
                os.remove(spideregg_file)
            except:
                pass

    def clean_fio_json_result(fio_json_file):
        with open(fio_json_file, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for l in lines:
                if "fio:" not in l:
                    f.write(l)
            f.truncate()
            f.close()

    if fio == 'y':
        sub.call(fio_command_generator(fio_rand_rw))
        clean_fio_json_result(fio_json_file)
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
            sub.call(fio_async_command_generator(fio_rand_rw))
            clean_fio_json_result(fio_json_file)
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
        print "\n\ncompleted random disk tests"

        sub.call(fio_command_generator(fio_seq_rw))
        clean_fio_json_result(fio_json_file)
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
            sub.call(fio_async_command_generator(fio_seq_rw))
            clean_fio_json_result(fio_json_file)
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
        print "\n\ncompleted sequential disk tests"

    if iperf == 'y':
        internal_net_csv_file = 'iperf_results.csv'
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time,
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            internal_network_data = (int(row[7]) / 1024) / 1024
            internal_network_bandwidth = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)
        print "\ncompleted internal network tests"

# ==================== GLOBAL TRANSMITTING ==================== #
    # Transmit data back to Olympus
    print "\n\n"
    print "Transmitting to Forecast db"
    print "\n\n"

    if geekbench == 'y':
        Open_Processordata = Processordata(
            vm_id=vm_id,
            cores_id=cores_id,
            os_id=os_id,
            processor=processor_info,
            performance=values['Total'],
            runtime=values['Runtime'],
            intmulti=values['Integer Multicore'],
            floatmulti=values['Floating Point Multicore'],
            totalmulti=values['Total'],
            intsingle=values['Integer Singlecore'],
            floatsingle=values['Floating Point Singlecore'],
            totalsingle=values['Total Single'],
            aes=values['AES'],
            twofish=values['Twofish'],
            sha1=values['SHA1'],
            sha2=values['SHA2'],
            bzipcompression=values['BZip2 Compress'],
            bzipdecompression=values['BZip2 Decompress'],
            jpegcompression=values['JPEG Compress'],
            jpegdecompression=values['JPEG Decompress'],
            pngcompression=values['PNG Compress'],
            pngdecompression=values['PNG Decompress'],
            sobel=values['Sobel'],
            lua=values['Lua'],
            dijkstra=values['Dijkstra'],
            blackscholes=values['BlackScholes'].split(' ')[0],
            mandelbrot=values['Mandelbrot'],
            sharpenimage=values['Sharpen Filter'],
            blurimage=values['Blur Filter'],
            sgemm=values['SGEMM'],
            dgemm=values['DGEMM'],
            sfft=values['SFFT'],
            dfft=values['DFFT'],
            nbody=values['N-Body'],
            raytrace=values['Ray Trace'])
        session.add(Open_Processordata)
        session.commit()

        Open_Memorydata = Memorydata(
            vm_id=vm_id,
            cores_id=cores_id,
            os_id=os_id,
            bandwidth=values['Stream Triad'],
            copy=values['Stream Copy'],
            scale=values['Stream Scale'],
            add=values['Stream Add'],
            triad=values['Stream Triad'],
            memsingle=values['Memory Singlecore'],
            memmulti=values['Memory Multicore'])
        session.add(Open_Memorydata)
        session.commit()

        print "Finished transferring geekbench results"

    if fio == 'y':

        Open_Localdiskdata = Localdiskdata(
            vm_id=vm_id,
            cores_id=cores_id,
            os_id=os_id,
            iops_read_rand=iops_read_rand,
            iops_write_rand=iops_write_rand,
            io_read_seq=io_read_seq,
            io_write_seq=io_write_seq,
            runtime_read_rand=runtime_read_rand,
            runtime_write_rand=runtime_write_rand,
            io_read_rand=io_read_rand,
            io_write_rand=io_write_rand,
            bw_read_rand=bw_read_rand,
            bw_write_rand=bw_write_rand,
            iops_read_seq=iops_read_seq,
            iops_write_seq=iops_write_seq,
            runtime_read_seq=runtime_read_seq,
            runtime_write_seq=runtime_write_seq,
            bw_read_seq=bw_read_seq,
            bw_write_seq=bw_write_seq,
            iops_read_seq_async=iops_read_seq_async,
            iops_read_rand_async=iops_read_rand_async,
            runtime_read_rand_async=runtime_read_rand_async,
            runtime_write_rand_async=runtime_write_rand_async,
            io_read_rand_async=io_read_rand_async,
            io_write_rand_async=io_write_rand_async,
            bw_read_rand_async=bw_read_rand_async,
            bw_write_rand_async=bw_write_rand_async,
            runtime_read_seq_async=runtime_read_seq_async,
            runtime_write_seq_async=runtime_write_seq_async,
            io_read_seq_async=io_read_seq_async,
            io_write_seq_async=io_write_seq_async,
            bw_read_seq_async=bw_read_seq_async,
            bw_write_seq_async=bw_write_seq_async)
        session.add(Open_Localdiskdata)
        session.commit()

        print "Finished transferring disk test results"

    if iperf == 'y':

        Open_Internalnetworkdata = Internalnetworkdata(
            vm_id=vm_id,
            cores_id=cores_id,
            os_id=os_id,
            single_threaded_throughput=internal_network_data,
            multi_threaded_throughput=internal_network_bandwidth)
        session.add(Open_Internalnetworkdata)
        session.commit()

        print "Finished transferring internal network test results"

    print "\n\n"
    print "All tests are successfully completed and the results are transferred to database"
    print "\n\n"

    iterator += 1
    sleep(sleeptime)
