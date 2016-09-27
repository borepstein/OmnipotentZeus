import os
import csv
import json
import platform
import subprocess as sub
from config import *
from datetime import datetime
from time import sleep, time
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict as od
from db import Base, Ignition, Processordata, Memorydata, Localdiskdata, Blockdiskdata, Internalnetworkdata, \
    Virtualmachine, Provider, Location, Operatingsystem, Cores, Disksizes

# Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
Session = sessionmaker(bind=Ignition)

# ==================== GLOBAL INTRODUCTION ==================== #
os.system('clear')
print "|------------------------|"
print "|    Omnipotent Hera     |"
print "|          v1.0          |"
print "|------------------------|"
print "\n"

# ==================== GLOBAL INSTALLER ==================== #
if geekbench == 'y':
    if not os.path.isfile(geekbench_install_dir + '/geekbench_x86_64'):
        os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz")
        os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
    os.chdir(geekbench_install_dir)
    sub.call(['./geekbench_x86_64', '-r', gb_email, gb_key])

if fio == 'y':
    os.system('apt-get install fio --yes')
if iperf == 'y':
    os.system('apt-get install iperf')


# ==================== RAW INPUT ==================== #
def get_id(table, key):
    session = Session()
    try:
        id = session.query(table.id).filter(table.key == key).one().id
    except Exception as e:
        print "\n------ Program terminated due to invalid input ------\n"
        exit()
    session.close()
    return id


def get_vm_id(table, vm_name, provider_id, location_id):
    session = Session()
    try:
        vm_id = session.query(table.id).filter(table.key == vm_name,
                                               table.provider_id == provider_id,
                                               table.location_id == location_id).one().id
    except Exception as e:
        print "\n------ Program terminated due to invalid input ------\n"
        exit()
    session.close()
    return vm_id


# Provider name
provider_name = raw_input("\nPlease enter the Provider: ")
provider_name = provider_name.lower()
provider_id = get_id(Provider, provider_name)

# Location
location_name = raw_input("\nPlease enter the Location: ")
location_name = location_name.lower()
location_id = get_id(Location, location_name)

# Virtual Machine
vm_name = raw_input("\nPlease enter the VM name: ")
vm_name = vm_name.lower()
vm_id = get_vm_id(Virtualmachine, vm_name, provider_id, location_id)

# Operating system
os_name = platform.system().lower()
os_id = get_id(Operatingsystem, os_name)

# Fetch CPU amount
v1 = sub.Popen(['cat', '/proc/cpuinfo'], stdout=sub.PIPE)
v2 = sub.Popen(['grep', 'processor'], stdin=v1.stdout, stdout=sub.PIPE)
v3 = sub.Popen(['wc', '-l'], stdin=v2.stdout, stdout=sub.PIPE)
core_count = v3.communicate()[0]
core_count = core_count.strip()

if core_count is '1':
    core_type = 'single'
elif core_count is '2':
    core_type = 'dual'
elif core_count is '4':
    core_type = 'quad'

# Cores
core_id = get_id(Cores, core_type)

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

if fio == 'y':
    disk_type = raw_input("\nPlease enter the Disk type (local / block): ")

    if disk_type.lower() == "local":
        fio_path = raw_input("\nPlease enter the Local storage path to run FIO test (Eg:- /home/mnt/): ")
    elif disk_type.lower() == "block":
        fio_path = raw_input("\nPlease enter the Block storage path to run FIO test (Eg:- /home/mnt/): ")
    else:
        print "\n------ Invalid entry for Disk type ------"
        exit()

    # Disk sizes
    disk_size = raw_input("\nPlease enter the Disk size: ")
    disk_size = disk_size.lower()
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
            print "\n------ Completed Geekbench test and transferred results to database ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== FIO ==================== #
    if fio == 'y':

        def fio_command_generator(option):
            global fio_command
            fio_command = ['fio', option, fio_filename, fio_blocksize, fio_filesize, fio_numjobs, fio_runtime,
                           fio_direct,
                           '-output-format=json', '-output=fio.json', '-time_based', '-group_reporting',
                           '-exitall']
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


        script_dir = os.getcwd()
        os.chmod(fio_path, 0775)
        os.chdir(fio_path)

        for fio_op_type in fio_op_types:

            sub.call(fio_command_generator(fio_op_type))
            clean_fio_json_result(fio_json_file)
            fio_json = open(fio_json_file)
            fio_data = json.load(fio_json)

            if fio_op_type is '-rw=write':

                iops_write_100_seq = str(fio_data['jobs'][0]['write']['iops'])
                throughput_write_100_seq = str(fio_data['jobs'][0]['write']['bw'])
                lat_write_100_seq = str(fio_data['jobs'][0]['write']['lat']['mean'])

            elif fio_op_type is '-rw=read':

                iops_read_100_seq = str(fio_data['jobs'][0]['read']['iops'])
                throughput_read_100_seq = str(fio_data['jobs'][0]['read']['bw'])
                lat_read_100_seq = str(fio_data['jobs'][0]['read']['lat']['mean'])

                spider_egg_exterminator()

            elif fio_op_type is '-rw=randwrite':

                iops_write_100_random = str(fio_data['jobs'][0]['write']['iops'])
                throughput_write_100_random = str(fio_data['jobs'][0]['write']['bw'])
                lat_write_100_random = str(fio_data['jobs'][0]['write']['lat']['mean'])

            elif fio_op_type is '-rw=randread':

                iops_read_100_random = str(fio_data['jobs'][0]['read']['iops'])
                throughput_read_100_random = str(fio_data['jobs'][0]['read']['bw'])
                lat_read_100_random = str(fio_data['jobs'][0]['read']['lat']['mean'])

                spider_egg_exterminator()

            elif fio_op_type is '-rw=rw':

                iops_read_random = str(fio_data['jobs'][0]['read']['iops'])
                iops_write_random = str(fio_data['jobs'][0]['write']['iops'])
                throughput_read_random = str(fio_data['jobs'][0]['read']['bw'])
                throughput_write_random = str(fio_data['jobs'][0]['write']['bw'])
                lat_read_random = str(fio_data['jobs'][0]['read']['lat']['mean'])
                lat_write_random = str(fio_data['jobs'][0]['write']['lat']['mean'])

                spider_egg_exterminator()

            elif fio_op_type is '-rw=randrw':

                iops_read_seq = str(fio_data['jobs'][0]['read']['iops'])
                iops_write_seq = str(fio_data['jobs'][0]['write']['iops'])
                throughput_read_seq = str(fio_data['jobs'][0]['read']['bw'])
                throughput_write_seq = str(fio_data['jobs'][0]['write']['bw'])
                lat_read_seq = str(fio_data['jobs'][0]['read']['lat']['mean'])
                lat_write_seq = str(fio_data['jobs'][0]['write']['lat']['mean'])

                spider_egg_exterminator()

        os.chdir(script_dir)
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
                print "\n\n------ Completed FIO disk tests and transferred results to database ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== IPERF ==================== #
    if iperf == 'y':
        # Single-threaded test
        internal_net_csv_file = 'iperf_results.csv'
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time,
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            single_threaded_throughput = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)

        # Multi-threaded test
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time, '-P', core_count,
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            multi_threaded_throughput = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)

        session = Session()
        try:
            Open_Internalnetworkdata = Internalnetworkdata(
                    vm_id=vm_id,
                    os_id=os_id,
                    single_threaded_throughput=single_threaded_throughput,
                    multi_threaded_throughput=multi_threaded_throughput)
            session.add(Open_Internalnetworkdata)
            session.commit()
            print "\n------ Completed iperf internal network test and transferred results to database ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    iterator += 1
    sleep(sleeptime)
