import os
import csv
import json
import shutil
import platform
import subprocess as sub
from conf import *
from datetime import datetime
from time import sleep, time
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict as od
from db import Base, Ignition, Processordata, Memorydata, Localdiskdata, Blockdiskdata, Internalnetworkdata, \
    Virtualmachine, Provider, Location, Operatingsystem, Cores, Disksizes

Base.metadata.bind = Ignition
Session = sessionmaker(bind=Ignition)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==================== GLOBAL INTRODUCTION ==================== #
os.system('clear')
print "|------------------------|"
print "|    Omnipotent Hera     |"
print "|        v2016.11        |"
print "|------------------------|"
print "\n"

# ==================== FETCH VM CONFIGURATION ==================== #
vm = ''
try:
    vm_data = json.load(open(os.path.join(BASE_DIR, 'vm_conf.json')))
    vm = vm_data['vm']
    provider_name = vm_data['provider']
    location_name = vm_data['location']
    vm_type = vm_data['vm_type']
    disk_type = vm_data['disk_type']
    fio_path = vm_data['fio_path']
    disk_size = vm_data['disk_size']
    internal_net_ip = vm_data['iperf_server']
except Exception as e:
    print "\n------ VM configuration does not exist. ------"
    exit()

# ==================== GLOBAL INSTALLER ==================== #
if operating_system == 'centos' or operating_system == 'redhat':
    if geekbench == 'y':
        geekbench_install_dir = "dist/Geekbench-3.1.2-Linux"
        gb_exe = '%s/%s' % (geekbench_install_dir, 'geekbench_x86_64')
        gb_tar = 'Geekbench-3.1.2-Linux.tar.gz'
        os.system('wget http://geekbench.s3.amazonaws.com/%s' % gb_tar)
        os.system('tar -xvzf %s' % gb_tar)
        os.remove(gb_tar)
        sub.call([os.path.join(BASE_DIR, gb_exe), '-r', gb_email, gb_key])
    if fio == 'y':
        os.system("wget ftp://rpmfind.net/linux/dag/redhat/el6/en/x86_64/dag/RPMS/fio-2.1.10-1.el6.rf.x86_64.rpm")
        os.system('rpm -iv fio-2.1.10-1.el6.rf.x86_64.rpm')
    if iperf == 'y':
        os.system('yum install iperf -y')

if operating_system == 'ubuntu' or operating_system == 'debian':
    if geekbench == 'y':
        geekbench_install_dir = "dist/Geekbench-3.1.2-Linux"
        gb_exe = '%s/%s' % (geekbench_install_dir, 'geekbench_x86_64')
        gb_tar = 'Geekbench-3.1.2-Linux.tar.gz'
        os.system('wget http://geekbench.s3.amazonaws.com/%s' % gb_tar)
        os.system('tar -xvzf %s' % gb_tar)
        os.remove(gb_tar)
        sub.call([os.path.join(BASE_DIR, gb_exe), '-r', gb_email, gb_key])
    if fio == 'y':
        os.system('apt-get install fio --yes')
    if iperf == 'y':
        os.system('apt-get install iperf')

# ==================== USER INPUT ==================== #
def sanitize_input(entity_name, table):
    while True:
        user_input = raw_input("\nPlease enter the %s: " % entity_name)
        if user_input == 'exit':
            exit()
        else:
            user_input = user_input.lower()
            id = get_id(table, user_input)

            if id is False:
                continue
            else:
                return id


def get_id(table, key):
    session = Session()
    try:
        id = session.query(table.id).filter(table.key == key).one().id
    except Exception as e:
        print "\n------ Invalid input. Try again. ------"
        return False

    session.close()
    return id


def get_vm_id(table, vm_name, provider_id, location_id):
    session = Session()
    try:
        vm_id = session.query(table.id).filter(table.key == vm_name,
                                               table.provider_id == provider_id,
                                               table.location_id == location_id).one().id
    except Exception as e:
        print "\n------ Invalid input. Try again. ------"
        return False

    session.close()
    return vm_id


# Provider name
if vm == '':
    provider_id = sanitize_input('Provider', Provider)
else:
    provider_name = provider_name.lower()
    provider_id = get_id(Provider, provider_name)

# Location
if vm == '':
    location_id = sanitize_input('Location', Location)
else:
    location_name = location_name.lower()
    location_id = get_id(Location, location_name)

# Virtual Machine
if vm == '':
    while True:
        vm_type = raw_input("\nPlease enter the VM type: ")
        if vm_type == 'exit':
            exit()
        else:
            vm_type = vm_type.lower()
            vm_id = get_vm_id(Virtualmachine, vm_type, provider_id, location_id)

            if vm_id is False:
                continue
            else:
                break
else:
    vm_type = vm_type.lower()
    vm_id = get_vm_id(Virtualmachine, vm_type, provider_id, location_id)

# Operating System
os_name = platform.system().lower()
os_id = get_id(Operatingsystem, os_name)

# CPU Cores
v1 = sub.Popen(['cat', '/proc/cpuinfo'], stdout=sub.PIPE)
v2 = sub.Popen(['grep', 'processor'], stdin=v1.stdout, stdout=sub.PIPE)
v3 = sub.Popen(['wc', '-l'], stdin=v2.stdout, stdout=sub.PIPE)
core_count = v3.communicate()[0]
core_count = int(core_count.strip())

if core_count == 1:
    core_type = 'single'
elif core_count == 2:
    core_type = 'dual'
elif core_count == 4:
    core_type = 'quad'
elif core_count == 8:
    core_type = 'oct'
elif core_count == 16:
    core_type = 'sixteen'
elif core_count == 30:
    core_type = 'thirty'
elif core_count == 32:
    core_type = 'thirtytwo'
elif core_count == 40:
    core_type = 'forty'

# Get Cores
core_id = get_id(Cores, core_type)

# RAM
r1 = sub.Popen(['cat', '/proc/meminfo'], stdout=sub.PIPE)
r2 = sub.Popen(['grep', 'MemTotal'], stdin=r1.stdout, stdout=sub.PIPE)
memoutput = r2.communicate()[0]
memoutput_list = memoutput.split(' ')
for x in memoutput_list:
    if x.isalnum():  # Converting from bytes to GB
        mem_count = int(x)
        mem_count = (mem_count / 1024.0 / 1024.0)
        ram_input = "%.2f" % mem_count

if fio == 'y':
    # Disk type
    if vm == '':
        while True:
            disk_type = raw_input("\nPlease enter the Disk type (local / block): ")
            if disk_type == 'exit':
                exit()
            elif disk_type.lower() == "local":
                fio_path = raw_input("\nPlease enter the Local storage path to run FIO test (Eg:- /mnt/): ")
                break
            elif disk_type.lower() == "block":
                fio_path = raw_input("\nPlease enter the Block storage path to run FIO test (Eg:- /mnt/): ")
                break
            else:
                print "\n------ Invalid input. Try again. ------"
                continue

    # Disk size
    if vm == '':
        disk_size_id = sanitize_input('Disk size', Disksizes)
    else:
        disk_size_id = get_id(Disksizes, disk_size)

    fio_op_types = ['-rw=write', '-rw=read', '-rw=randwrite', '-rw=randread', '-rw=rw', '-rw=randrw']

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

if iperf == 'y':
    # Internal network IP
    if vm == '':
        internal_net_ip = raw_input("\nPlease enter the IP address of the server you are trying to connect to: ")

    internal_net_csv = "C"

# ==================== GLOBAL TESTING ==================== #
start_date = datetime.now().strftime('%Y%m%d-%H%M')
iterator = 1
start = time()
for x in range(iterations):
    stop = time() - start
    if stop >= duration:
        break

    print "\n#######################################################\n"
    print "                    Iteration: " + str(iterator)
    print "\n#######################################################\n"

    iteration_start_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    # ==================== GEEKBENCH ==================== #
    if geekbench == 'y':
        gb_output = 'gb.json'
        # Run Geekbench
        sub.call([os.path.join(BASE_DIR, gb_exe), '--no-upload', '--export-json', gb_output])

        geekbench_json = open(gb_output)
        data = json.load(geekbench_json)
        if iterator == 1:
            processor_info = str(data['metrics'][6]['value'])

        # Parse Geekbench results
        y = 0
        scores = {}
        for x in range(0, 13, 1):
            z = str(data['sections'][0]['workloads'][y]['name'])
            scores[z] = str(data['sections'][0]['workloads'][y]['results'][1]['rate_string'])
            y += 1
        y = 0
        for x in range(0, 10, 1):
            z = str(data['sections'][1]['workloads'][y]['name'])
            scores[z] = str(data['sections'][1]['workloads'][y]['results'][1]['rate_string'])
            y += 1
        y = 0
        for x in range(0, 4, 1):
            z = str(data['sections'][2]['workloads'][y]['name'])
            scores[z] = str(data['sections'][2]['workloads'][y]['results'][1]['rate_string'])
            y += 1
        y = 0
        for x in range(0, 3, 1):
            z = str(data['sections'][y]['name']) + " Multicore"
            scores[z] = str(data['sections'][y]['multicore_score'])
            y += 1
        y = 0
        for x in range(0, 3, 1):
            z = str(data['sections'][y]['name']) + " Singlecore"
            scores[z] = str(data['sections'][y]['score'])
            y += 1
        y = 0
        for x in range(0, 1):
            z = "Total"
            scores[z] = str(data['multicore_score'])
            y += 1
        for x in range(0, 1):
            z = "Total Single"
            scores[z] = str(data['score'])
            y += 1
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
            elif " " in val:
                values[key] = float(val.split()[0])
            else:
                values[key] = val
            y = y + 1
        values = od(values)
        os.remove(gb_output)

        # Save Geekbench results to database
        session = Session()
        try:
            Open_Processordata = Processordata(
                    vm_id=vm_id,
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
            print "\n------ Completed GEEKBENCH ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    # ==================== FIO ==================== #
    def fio_command_generator(option):
        """
        This function generates the command to run FIO from a set of input arguments and saves the output in txt format
        """
        global fio_command
        fio_command = ['fio', option, fio_filename, fio_blocksize, fio_filesize, fio_numjobs, fio_runtime, fio_direct,
                       '-output-format=json', '-output=fio.json', '-time_based', '-group_reporting', '-exitall']
        print "\n"
        return fio_command


    def spider_egg_exterminator():
        """
        This function deletes all dummy files created during FIO test
        """
        fio_json.close()
        os.remove(fio_json_file)
        for baby_spiders in range(0, spider_hatchlings):
            spideregg_file = "spider_eggs." + str(baby_spiders) + ".0"
            try:
                os.remove(spideregg_file)
            except:
                pass


    def convert_fio_json_result(fio_json_file):
        """
        This function converts the JSON output file to required format to fetch data easily
        """
        with open(fio_json_file, "r+") as f:
            lines = f.readlines()
            f.seek(0)
            for l in lines:
                if "fio:" not in l:
                    f.write(l)
            f.truncate()
            f.close()


    if fio == 'y':

        os.chmod(fio_path, 0775)  # Set permission for the FIO path
        os.chdir(fio_path)  # Change directory to FIO path

        for fio_op_type in fio_op_types:
            # Run FIO
            sub.call(fio_command_generator(fio_op_type))

            # Convert generated JSON output file to required format
            convert_fio_json_result(fio_json_file)

            # Parse FIO results
            fio_json = open(fio_json_file)
            fio_data = json.load(fio_json)

            # Sequential Write
            if fio_op_type is '-rw=write':

                iops_write_100_seq = str(fio_data['jobs'][0]['write']['iops'])
                throughput_write_100_seq = str(fio_data['jobs'][0]['write']['bw'])
                lat_write_100_seq = str(fio_data['jobs'][0]['write']['lat']['mean'])

            # Sequential Read
            elif fio_op_type is '-rw=read':

                iops_read_100_seq = str(fio_data['jobs'][0]['read']['iops'])
                throughput_read_100_seq = str(fio_data['jobs'][0]['read']['bw'])
                lat_read_100_seq = str(fio_data['jobs'][0]['read']['lat']['mean'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

            # Random Write
            elif fio_op_type is '-rw=randwrite':

                iops_write_100_random = str(fio_data['jobs'][0]['write']['iops'])
                throughput_write_100_random = str(fio_data['jobs'][0]['write']['bw'])
                lat_write_100_random = str(fio_data['jobs'][0]['write']['lat']['mean'])

            # Random Read
            elif fio_op_type is '-rw=randread':

                iops_read_100_random = str(fio_data['jobs'][0]['read']['iops'])
                throughput_read_100_random = str(fio_data['jobs'][0]['read']['bw'])
                lat_read_100_random = str(fio_data['jobs'][0]['read']['lat']['mean'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

            # Sequential Read Write
            elif fio_op_type is '-rw=rw':

                iops_read_random = str(fio_data['jobs'][0]['read']['iops'])
                iops_write_random = str(fio_data['jobs'][0]['write']['iops'])
                throughput_read_random = str(fio_data['jobs'][0]['read']['bw'])
                throughput_write_random = str(fio_data['jobs'][0]['write']['bw'])
                lat_read_random = str(fio_data['jobs'][0]['read']['lat']['mean'])
                lat_write_random = str(fio_data['jobs'][0]['write']['lat']['mean'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

            # Random Read Write
            elif fio_op_type is '-rw=randrw':

                iops_read_seq = str(fio_data['jobs'][0]['read']['iops'])
                iops_write_seq = str(fio_data['jobs'][0]['write']['iops'])
                throughput_read_seq = str(fio_data['jobs'][0]['read']['bw'])
                throughput_write_seq = str(fio_data['jobs'][0]['write']['bw'])
                lat_read_seq = str(fio_data['jobs'][0]['read']['lat']['mean'])
                lat_write_seq = str(fio_data['jobs'][0]['write']['lat']['mean'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

        os.chdir(BASE_DIR)  # Change directory back to script path

        # Save FIO results to database
        session = Session()
        try:
            if disk_type.lower() == "local":
                Open_Localdiskdata = Localdiskdata(
                        vm_id=vm_id,
                        os_id=os_id,
                        iops_write_100_seq=iops_write_100_seq,
                        throughput_write_100_seq=throughput_write_100_seq,
                        lat_write_100_seq=lat_write_100_seq,
                        iops_read_100_seq=iops_read_100_seq,
                        throughput_read_100_seq=throughput_read_100_seq,
                        lat_read_100_seq=lat_read_100_seq,
                        iops_write_100_random=iops_write_100_random,
                        throughput_write_100_random=throughput_write_100_random,
                        lat_write_100_random=lat_write_100_random,
                        iops_read_100_random=iops_read_100_random,
                        throughput_read_100_random=throughput_read_100_random,
                        lat_read_100_random=lat_read_100_random,
                        iops_read_random=iops_read_random,
                        iops_write_random=iops_write_random,
                        throughput_read_random=throughput_read_random,
                        throughput_write_random=throughput_write_random,
                        iops_read_seq=iops_read_seq,
                        iops_write_seq=iops_write_seq,
                        throughput_read_seq=throughput_read_seq,
                        throughput_write_seq=throughput_write_seq,
                        latency_read_seq=lat_read_seq,
                        latency_write_seq=lat_write_seq,
                        latency_read_random=lat_read_random,
                        latency_write_random=lat_write_random)
                session.add(Open_Localdiskdata)
                session.commit()

            elif disk_type.lower() == "block":
                Open_Blockdiskdata = Blockdiskdata(
                        vm_id=vm_id,
                        disk_size_id=disk_size_id,
                        os_id=os_id,
                        iops_write_100_seq=iops_write_100_seq,
                        throughput_write_100_seq=throughput_write_100_seq,
                        lat_write_100_seq=lat_write_100_seq,
                        iops_read_100_seq=iops_read_100_seq,
                        throughput_read_100_seq=throughput_read_100_seq,
                        lat_read_100_seq=lat_read_100_seq,
                        iops_write_100_random=iops_write_100_random,
                        throughput_write_100_random=throughput_write_100_random,
                        lat_write_100_random=lat_write_100_random,
                        iops_read_100_random=iops_read_100_random,
                        throughput_read_100_random=throughput_read_100_random,
                        lat_read_100_random=lat_read_100_random,
                        iops_read_random=iops_read_random,
                        iops_write_random=iops_write_random,
                        throughput_read_random=throughput_read_random,
                        throughput_write_random=throughput_write_random,
                        iops_read_seq=iops_read_seq,
                        iops_write_seq=iops_write_seq,
                        throughput_read_seq=throughput_read_seq,
                        throughput_write_seq=throughput_write_seq,
                        latency_read_seq=lat_read_seq,
                        latency_write_seq=lat_write_seq,
                        latency_read_random=lat_read_random,
                        latency_write_random=lat_write_random)
                session.add(Open_Blockdiskdata)
                session.commit()
                print "\n\n------ Completed FIO ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== IPERF ==================== #
    if iperf == 'y':
        internal_net_csv_file = 'iperf_results.csv'

        # Start iperf server on iperf server machine
        os.system('ssh -i %s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no ubuntu@%s screen -md iperf -s' % (
        os.path.join(BASE_DIR, 'saltkey.pem'), internal_net_ip))

        # Start iperf client in single threaded mode
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time,
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        # Parse iperf results
        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            single_threaded_throughput = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)

        # Start iperf client in multi threaded mode
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time, '-P', str(core_count),
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            multi_threaded_throughput = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)

        # Save iperf results to database
        session = Session()
        try:
            Open_Internalnetworkdata = Internalnetworkdata(
                    vm_id=vm_id,
                    os_id=os_id,
                    single_threaded_throughput=single_threaded_throughput,
                    multi_threaded_throughput=multi_threaded_throughput)
            session.add(Open_Internalnetworkdata)
            session.commit()
            print "\n------ Completed IPERF ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    print "\nIteration %s completed\n" % iterator

    iterator += 1
    sleep(sleep_time)  # Any delay before the next round is executed

# Remove Geekbench dist folder
os.chdir(BASE_DIR)
shutil.rmtree('dist')

print "----------------------------------------------------------------------------------"
print " All tests are successfully completed and the results are transferred to database "
print "----------------------------------------------------------------------------------"
