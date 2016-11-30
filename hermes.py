import os
import csv
import json
import shutil
import socket
import subprocess as sub
from conf import *
from random import randint
from urllib2 import urlopen
from time import sleep, time
from datetime import datetime
from collections import OrderedDict as od
from prometheus import Base, Olympus
from prometheus import Ignition
from sqlalchemy.orm import sessionmaker

# Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
Session = sessionmaker(bind=Ignition)
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# ==================== GLOBAL INTRODUCTION ==================== #
os.system('clear')
print "|------------------------|"
print "|    Omnipotent Zeus     |"
print "|        v2016.11        |"
print "|------------------------|"
print "\n"
print "Project Olympus is designed to be a testbed for measuring virtual machine performance in a scalable, \
cloud environment. The design of Olympus is its flexibility in continuous testing over time, rather than \
spot testing, which is an archaic method that cannot apply to highly variable environments with multiple \
(many of which are possibly uncontrolled) variables.\n\n"
sleep(2)

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
    if apachebench == 'y':
        os.system('yum install httpd-tools')
    if iozone == 'y':
        os.system("wget http://www.iozone.org/src/current/iozone-3-338.i386.rpm")
        os.system("rpm -ivh iozone-3-338.i386.rpm")
    if sysbench == 'y':
        os.system('yum -y install sysbench')

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
    if apachebench == 'y':
        os.system('apt-get install apache2-utils')
    if iozone == 'y':
        os.system('apt-get install iozone3')
    if sysbench == 'y':
        os.system('apt-get install sysbench')

# ==================== INITIALIZATION ==================== #
processor_info = ""

# CPU Cores
v1 = sub.Popen(['cat', '/proc/cpuinfo'], stdout=sub.PIPE)
v2 = sub.Popen(['grep', 'processor'], stdin=v1.stdout, stdout=sub.PIPE)
v3 = sub.Popen(['wc', '-l'], stdin=v2.stdout, stdout=sub.PIPE)
cpu_count = v3.communicate()[0]

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

# Hostname
try:
    vm_hostname = socket.gethostname()
    if not vm_hostname:
        vm_hostname = urlopen('http://ip.42.pl/raw').read()
except Exception as e:
    vm_hostname = "N/A"

if fio == 'y':
    fio_op_types = ['-rw=write', '-rw=read', '-rw=randwrite', '-rw=randread', '-rw=rw', '-rw=randrw']
    fio_rw = "Yes"
    fio_seq = "Yes"

    fio_blocksize = '-bs=' + blocksize + 'k'
    fio_filesize = '-size=' + filesize + "M"
    numjobs = cpu_count  # Number of threads should be equal to number of CPUs
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
else:
    fio_rw = "N/A"
    fio_seq = "N/A"
    fio_blocksize = 0
    fio_filesize = 0
    fio_numjobs = 0
    fio_direct_val = 0

if iozone == 'y':
    spider_hatchlings = int(numjobs) + 1
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
    sysbench_io_mode = 'sync'
    if direct_io == 'y':
        sysbench_direct = '--file-extra-flags=direct'
    else:
        sysbench_direct = ''

if spec == 'y':
    spec_tests = ['400.perlbench', '401.bzip2', '403.gcc', '429.mcf', '483.xalancbmk', '450.soplex', '482.sphinx3']

    spec_result_dir = '/SPEC/CPU2006/result'
    spec_output_dir = '/SPEC/CPU2006/output'
    int_result_csv = 'CINT2006.001.ref.csv'
    fp_result_csv = 'CFP2006.001.ref.csv'
    csv_results = [int_result_csv, fp_result_csv]

# ================ COLLECT INFORMATION ON THE PROVIDER AND VM ENVIRONMENT =============== #
provider_input = raw_input("\nPlease enter the provider's name: ")
provider_input = provider_input.lower()
provider_region = "N/A"

vmcount_input = raw_input(
        "\nWhich VM copy is this? (i.e., you need to test 3 of each machine for 24 hours. Is this machine 1, 2, or 3?) ")
local_input = "0"
block_input = "0"

if fio == 'y':
    fio_path = raw_input("\nPlease enter the storage path to run FIO (Eg:- /mnt/): ")

if iperf == 'y':
    internal_net_ip = raw_input('\nPlease enter the IP address of the iperf server you are trying to connect to: ')
    internal_net_csv = "C"

startdate_input = datetime.now().strftime('%Y%m%d-%H%M')
# Generate a random number to add to the unique ID for this provider and VM combination in the test cycle
random_uid = randint(0, 1000000)
generated_uid = provider_input + vm_hostname + startdate_input + str(random_uid)

# ==================== GLOBAL TESTING ==================== #
iterator = 1
start = time()
for x in range(iterations):
    stop = time() - start
    if stop >= duration:
        break

    print "\n#######################################################\n"
    print "                    Iteration: " + str(iterator)
    print "\n#######################################################\n"

    os.chdir(BASE_DIR)
    iteration_start_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    session = Session()
    try:
        Open_Olympus = Olympus(
                project=project_id,
                uid=generated_uid,
                provider=provider_input,
                region=provider_region,
                startdate=startdate_input,
                iteration=iterator,
                iteration_start_time=iteration_start_time,
                vm=vm_hostname,
                vmcount=vmcount_input,
                vcpu=cpu_count,
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
        print "Basic information transfer complete\n"
    except Exception as e:
        session.rollback()
        raise e

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


    def fio_async_command_generator(option):
        """
        This function generates the command to run FIO ASYNC from a set of input arguments and saves the output in txt
        format
        """
        global fio_command
        fio_command = ['fio', option, fio_filename, fio_blocksize, fio_filesize, fio_numjobs, fio_runtime, fio_direct,
                       '-output-format=json', '-output=fio.json', '-time_based', '-group_reporting',
                       '-iodepth=32', '-ioengine=libaio', '-exitall']
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

                iops_write_100_rand = str(fio_data['jobs'][0]['write']['iops'])
                throughput_write_100_rand = str(fio_data['jobs'][0]['write']['bw'])
                lat_write_100_rand = str(fio_data['jobs'][0]['write']['lat']['mean'])

            # Random Read
            elif fio_op_type is '-rw=randread':

                iops_read_100_rand = str(fio_data['jobs'][0]['read']['iops'])
                throughput_read_100_rand = str(fio_data['jobs'][0]['read']['bw'])
                lat_read_100_rand = str(fio_data['jobs'][0]['read']['lat']['mean'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

            # Sequential Read Write
            elif fio_op_type is '-rw=rw':
                runtime_read_seq = str(fio_data['jobs'][0]['read']['runtime'])
                runtime_write_seq = str(fio_data['jobs'][0]['write']['runtime'])
                io_read_seq = str(fio_data['jobs'][0]['read']['io_bytes'])
                io_write_seq = str(fio_data['jobs'][0]['write']['io_bytes'])
                iops_read_seq = str(fio_data['jobs'][0]['read']['iops'])
                iops_write_seq = str(fio_data['jobs'][0]['write']['iops'])
                bw_read_seq = str(fio_data['jobs'][0]['read']['bw'])
                bw_write_seq = str(fio_data['jobs'][0]['write']['bw'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

            # Random Read Write
            elif fio_op_type is '-rw=randrw':

                runtime_read_rand = str(fio_data['jobs'][0]['read']['runtime'])
                runtime_write_rand = str(fio_data['jobs'][0]['write']['runtime'])
                io_read_rand = str(fio_data['jobs'][0]['read']['io_bytes'])
                io_write_rand = str(fio_data['jobs'][0]['write']['io_bytes'])
                iops_read_rand = str(fio_data['jobs'][0]['read']['iops'])
                iops_write_rand = str(fio_data['jobs'][0]['write']['iops'])
                bw_read_rand = str(fio_data['jobs'][0]['read']['bw'])
                bw_write_rand = str(fio_data['jobs'][0]['write']['bw'])

                spider_egg_exterminator()  # Delete dummy files created during FIO test

        # Run FIO Asynchronous mode if async_io is enabled
        if async_io == 'y':

            for fio_op_type in fio_op_types:

                # Run FIO in Asynchronous mode
                sub.call(fio_async_command_generator(fio_op_type))

                # Convert generated JSON output file to required format
                convert_fio_json_result(fio_json_file)

                # Parse FIO async results
                fio_json = open(fio_json_file)
                fio_data = json.load(fio_json)

                # Asynchronous Sequential Write
                if fio_op_type is '-rw=write':

                    iops_write_100_seq_async = str(fio_data['jobs'][0]['write']['iops'])
                    throughput_write_100_seq_async = str(fio_data['jobs'][0]['write']['bw'])
                    lat_write_100_seq_async = str(fio_data['jobs'][0]['write']['lat']['mean'])

                # Asynchronous Sequential Read
                elif fio_op_type is '-rw=read':

                    iops_read_100_seq_async = str(fio_data['jobs'][0]['read']['iops'])
                    throughput_read_100_seq_async = str(fio_data['jobs'][0]['read']['bw'])
                    lat_read_100_seq_async = str(fio_data['jobs'][0]['read']['lat']['mean'])

                    spider_egg_exterminator()  # Delete dummy files created during FIO test

                # Asynchronous Random Write
                elif fio_op_type is '-rw=randwrite':

                    iops_write_100_rand_async = str(fio_data['jobs'][0]['write']['iops'])
                    throughput_write_100_rand_async = str(fio_data['jobs'][0]['write']['bw'])
                    lat_write_100_rand_async = str(fio_data['jobs'][0]['write']['lat']['mean'])

                # Asynchronous Random Read
                elif fio_op_type is '-rw=randread':

                    iops_read_100_rand_async = str(fio_data['jobs'][0]['read']['iops'])
                    throughput_read_100_rand_async = str(fio_data['jobs'][0]['read']['bw'])
                    lat_read_100_rand_async = str(fio_data['jobs'][0]['read']['lat']['mean'])

                    spider_egg_exterminator()  # Delete dummy files created during FIO test

                # Asynchronous Sequential Read Write
                elif fio_op_type is '-rw=rw':
                    runtime_read_seq_async = str(fio_data['jobs'][0]['read']['runtime'])
                    runtime_write_seq_async = str(fio_data['jobs'][0]['write']['runtime'])
                    io_read_seq_async = str(fio_data['jobs'][0]['read']['io_bytes'])
                    io_write_seq_async = str(fio_data['jobs'][0]['write']['io_bytes'])
                    iops_read_seq_async = str(fio_data['jobs'][0]['read']['iops'])
                    iops_write_seq_async = str(fio_data['jobs'][0]['write']['iops'])
                    bw_read_seq_async = str(fio_data['jobs'][0]['read']['bw'])
                    bw_write_seq_async = str(fio_data['jobs'][0]['write']['bw'])

                    spider_egg_exterminator()  # Delete dummy files created during FIO test

                # Asynchronous Random Read Write
                elif fio_op_type is '-rw=randrw':

                    runtime_read_rand_async = str(fio_data['jobs'][0]['read']['runtime'])
                    runtime_write_rand_async = str(fio_data['jobs'][0]['write']['runtime'])
                    io_read_rand_async = str(fio_data['jobs'][0]['read']['io_bytes'])
                    io_write_rand_async = str(fio_data['jobs'][0]['write']['io_bytes'])
                    iops_read_rand_async = str(fio_data['jobs'][0]['read']['iops'])
                    iops_write_rand_async = str(fio_data['jobs'][0]['write']['iops'])
                    bw_read_rand_async = str(fio_data['jobs'][0]['read']['bw'])
                    bw_write_rand_async = str(fio_data['jobs'][0]['write']['bw'])

                    spider_egg_exterminator()  # Delete dummy files created during FIO test

        os.chdir(BASE_DIR)  # Change directory back to script path

        # Save FIO results to database
        session = Session()
        try:
            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.iops_read_rand: iops_read_rand,
                Olympus.iops_write_rand: iops_write_rand,
                Olympus.io_read_rand: io_read_rand,
                Olympus.io_write_rand: io_write_rand,
                Olympus.runtime_read_rand: runtime_read_rand,
                Olympus.runtime_write_rand: runtime_write_rand,
                Olympus.bw_read_rand: bw_read_rand,
                Olympus.bw_write_rand: bw_write_rand,
                Olympus.iops_read_100_rand: iops_read_100_rand,
                Olympus.iops_write_100_rand: iops_write_100_rand,
                Olympus.throughput_read_100_rand: throughput_read_100_rand,
                Olympus.throughput_write_100_rand: throughput_write_100_rand,
                Olympus.lat_read_100_rand: lat_read_100_rand,
                Olympus.lat_write_100_rand: lat_write_100_rand,
                Olympus.iops_read_seq: iops_read_seq,
                Olympus.iops_write_seq: iops_write_seq,
                Olympus.io_read_seq: io_read_seq,
                Olympus.io_write_seq: io_write_seq,
                Olympus.runtime_read_seq: runtime_read_seq,
                Olympus.runtime_write_seq: runtime_write_seq,
                Olympus.bw_read_seq: bw_read_seq,
                Olympus.bw_write_seq: bw_write_seq,
                Olympus.iops_read_100_seq: iops_read_100_seq,
                Olympus.iops_write_100_seq: iops_write_100_seq,
                Olympus.throughput_read_100_seq: throughput_read_100_seq,
                Olympus.throughput_write_100_seq: throughput_write_100_seq,
                Olympus.lat_read_100_seq: lat_read_100_seq,
                Olympus.lat_write_100_seq: lat_write_100_seq
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
                    Olympus.bw_write_rand_async: bw_write_rand_async,
                    Olympus.iops_read_100_rand_async: iops_read_100_rand_async,
                    Olympus.iops_write_100_rand_async: iops_write_100_rand_async,
                    Olympus.throughput_read_100_rand_async: throughput_read_100_rand_async,
                    Olympus.throughput_write_100_rand_async: throughput_write_100_rand_async,
                    Olympus.lat_read_100_rand_async: lat_read_100_rand_async,
                    Olympus.lat_write_100_rand_async: lat_write_100_rand_async,
                    Olympus.iops_read_seq_async: iops_read_seq_async,
                    Olympus.iops_write_seq_async: iops_write_seq_async,
                    Olympus.io_read_seq_async: io_read_seq_async,
                    Olympus.io_write_seq_async: io_write_seq_async,
                    Olympus.runtime_read_seq_async: runtime_read_seq_async,
                    Olympus.runtime_write_seq_async: runtime_write_seq_async,
                    Olympus.bw_read_seq_async: bw_read_seq_async,
                    Olympus.bw_write_seq_async: bw_write_seq_async,
                    Olympus.iops_read_100_seq_async: iops_read_100_seq_async,
                    Olympus.iops_write_100_seq_async: iops_write_100_seq_async,
                    Olympus.throughput_read_100_seq_async: throughput_read_100_seq_async,
                    Olympus.throughput_write_100_seq_async: throughput_write_100_seq_async,
                    Olympus.lat_read_100_seq_async: lat_read_100_seq_async,
                    Olympus.lat_write_100_seq_async: lat_write_100_seq_async
                })
                session.commit()
            print "\n------ Completed FIO ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    if iperf == 'y':
        internal_net_csv_file = 'iperf_results.csv'

        # Run iperf
        sub.call(['iperf', '-c', internal_net_ip, '-t', internal_net_time,
                  '-y', internal_net_csv], stdout=open(internal_net_csv_file, "w"))

        # Parse iperf results
        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            internal_network_data = (int(row[7]) / 1024) / 1024
            internal_network_bandwidth = (int(row[8]) / 1024) / 1024
        os.remove(internal_net_csv_file)

        # Save iperf results to database
        session = Session()
        try:
            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.internal_network_data: internal_network_data,
                Olympus.internal_network_bandwidth: internal_network_bandwidth
            })
            session.commit()
            print "\n------ Completed IPERF ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    if apachebench == 'y':
        ab_results = "ab_results.txt"
        ab_address = ab_hostname
        if ab_port:
            ab_address = ab_address + ":" + ab_port
        if ab_path:
            ab_address = ab_address + ab_path

        # Run Apachebench
        sub.call(['ab', '-q', '-n', ab_requests, '-c', ab_concurrency, '-s', ab_timeout,
                  '-e', ab_results, ab_address], stdout=open(ab_results, "w"))

        # Parse Apachebench results
        with open(ab_results) as f:
            lines = f.readlines()
            for l in lines:
                if ("Requests per second" in l):
                    requests_per_sec = filter(None, l.split(" "))[3]
                if ("Time taken for tests:" in l):
                    time_taken = filter(None, l.split(" "))[4]
                if ("50%" in l):
                    percent_50 = filter(None, l.split(" "))[1]
                if ("66%" in l):
                    percent_66 = filter(None, l.split(" "))[1]
                if ("75%" in l):
                    percent_75 = filter(None, l.split(" "))[1]
                if ("80%" in l):
                    percent_80 = filter(None, l.split(" "))[1]
                if ("90%" in l):
                    percent_90 = filter(None, l.split(" "))[1]
                if ("95%" in l):
                    percent_95 = filter(None, l.split(" "))[1]
                if ("98%" in l):
                    percent_98 = filter(None, l.split(" "))[1]
                if ("99%" in l):
                    percent_99 = filter(None, l.split(" "))[1]
                if ("100%" in l):
                    percent_100 = filter(None, l.split(" "))[1]

        os.remove(ab_results)

        # Save Apachebench results to database
        session = Session()
        try:
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
            print "\n------ Completed APACHEBENCH ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def iozone_dummy_exterminator():
        """
        This function deletes all dummy files created during IOZONE test
        """
        for iozone_dummy in range(0, spider_hatchlings - 1):
            iozone_dummy_file = "iozone.DUMMY." + str(iozone_dummy)
            try:
                os.remove(iozone_dummy_file)
            except:
                pass


    def iozone_result_parser(result_file, target_var):
        """
        This function parses IOZONE results from txt output
        """
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
        # Sequential Write
        iozone_results = 'iozone_seq_write_results.txt'
        os.system('iozone %s -t %s -O -r %s -s %s -w -i 0 > %s' %
                  (iozone_direct, iozone_numjobs, iozone_blocksize, iozone_filesize, iozone_results))
        target_var = "initial writers"
        iozone_seq_writers = iozone_result_parser(iozone_results, target_var)
        target_var = "rewriters"
        iozone_seq_rewriters = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        # Sequential Read
        iozone_results = 'iozone_seq_read_results.txt'
        os.system('iozone %s -t %s -M -O -r %s -s %s -w -i 1 > %s' %
                  (iozone_direct, iozone_numjobs, iozone_blocksize, iozone_filesize, iozone_results))
        target_var = "readers"
        iozone_seq_readers = iozone_result_parser(iozone_results, target_var)
        target_var = "re-readers"
        iozone_seq_rereaders = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        # Random Read / Write
        iozone_results = 'iozone_rand_results.txt'
        os.system('iozone %s -t %s -M -O -r %s -s %s -w -i 2 > %s' %
                  (iozone_direct, iozone_numjobs, iozone_blocksize, iozone_filesize, iozone_results))
        target_var = "random readers"
        iozone_random_readers = iozone_result_parser(iozone_results, target_var)
        target_var = "random writers"
        iozone_random_writers = iozone_result_parser(iozone_results, target_var)
        os.remove(iozone_results)

        iozone_dummy_exterminator()  # Delete dummy files created during IOZONE test

        # Save IOZONE results to database
        session = Session()
        try:
            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.iozone_seq_writers: iozone_seq_writers,
                Olympus.iozone_seq_rewriters: iozone_seq_rewriters,
                Olympus.iozone_seq_readers: iozone_seq_readers,
                Olympus.iozone_seq_rereaders: iozone_seq_rereaders,
                Olympus.iozone_random_readers: iozone_random_readers,
                Olympus.iozone_random_writers: iozone_random_writers,
            })

            session.commit()
            print "\n------ Completed IOZONE ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def sysbench_command_generator(sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs,
                                   sysbench_io_mode, sysbench_test_mode, sysbench_runtime, sysbench_results):
        """
        This function generates the command to run Sysbench from a set of arguments and saves the output in txt format
        """

        sysbench_command = 'sysbench %s --test=fileio --file-total-size=%s --file-block-size=%s \
        --file-num=%s --num-threads=%s --file-io-mode=%s --file-test-mode=%s --max-time=%s run > %s' % (
            sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_numjobs,
            sysbench_io_mode, sysbench_test_mode, sysbench_runtime, sysbench_results)

        return sysbench_command


    def sysbench_result_parser(sysbench_results, sysbench_test_mode):
        """
        This function parses Sysbench results from txt output
        """
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

        # Sequential Write
        sysbench_test_mode = 'seqwr'
        sysbench_command = sysbench_command_generator(
                sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
                sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_seq_write = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)

        # Sequential Read
        sysbench_test_mode = 'seqrd'
        sysbench_command = sysbench_command_generator(
                sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
                sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_seq_read = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)
        os.system('sysbench --test=fileio --file-total-size=%s --file-num=%s cleanup' %
                  (sysbench_filesize, sysbench_numjobs))

        # Random Write
        sysbench_test_mode = 'rndwr'
        sysbench_command = sysbench_command_generator(
                sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
                sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_rand_write = sysbench_result_parser(sysbench_results, sysbench_test_mode)
        os.remove(sysbench_results)

        # Random Read
        sysbench_test_mode = 'rndrd'
        sysbench_command = sysbench_command_generator(
                sysbench_direct, sysbench_filesize, sysbench_blocksize, sysbench_numjobs, sysbench_io_mode,
                sysbench_test_mode, sysbench_runtime, sysbench_results)
        os.system(sysbench_command)
        sysbench_rand_read = sysbench_result_parser(sysbench_results, sysbench_test_mode)

        # Remove Sysbench output file and all the dummy files created during the test
        os.remove(sysbench_results)
        os.system('sysbench --test=fileio --file-total-size=%s --file-num=%s cleanup' %
                  (sysbench_filesize, sysbench_numjobs))

        # Save Sysbench results to database
        session = Session()
        try:
            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.sysbench_seq_write: sysbench_seq_write,
                Olympus.sysbench_seq_read: sysbench_seq_read,
                Olympus.sysbench_rand_write: sysbench_rand_write,
                Olympus.sysbench_rand_read: sysbench_rand_read
            })

            session.commit()
            print "\n------ Completed SYSBENCH ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


    def run_spec_suite():
        """
        This function runs SPEC test and saves output in csv format
        """
        try:
            spec_cmd = ['runspec', '--config', 'spec_test_config.cfg', '--tune', 'all', '--rate', cpu_count,
                        '--noreportable',
                        '--output_format', 'csv', '--iterations', '1']
            spec_cmd.extend(spec_tests)
            sub.call(spec_cmd)
        except Exception as e:
            raise e

    def parse_spec_results():
        """
        This function parses SPEC results from csv output
        """
        os.chdir(spec_result_dir)

        for csv_result in csv_results:
            for item in spec_tests:
                with open(csv_result, 'rb') as f:
                    csv_handler = csv.reader(f)
                    for row in csv_handler:
                        if item in row:
                            results["%s_base_copies" % item] = row[1] if row[1] is not None else ''
                            results["%s_base_runtime" % item] = row[2] if row[2] is not None else ''
                            results["%s_base_rate" % item] = row[3] if row[3] is not None else ''
                            results["%s_peak_copies" % item] = row[6] if row[6] is not None else ''
                            results["%s_peak_runtime" % item] = row[7] if row[7] is not None else ''
                            results["%s_peak_rate" % item] = row[8] if row[8] is not None else ''
                            break
        return


    if spec == 'y':
        results = {}

        if os.path.exists(spec_result_dir):
            shutil.rmtree(spec_result_dir)

        if not os.path.exists(spec_output_dir):
            os.makedirs(spec_output_dir)

        # Run SPEC
        run_spec_suite()

        # Parse SPEC results
        os.system(
                'cp %s/%s %s/%s_%s_INT.csv' % (spec_result_dir, int_result_csv, spec_output_dir, project_id, iterator))
        os.system('cp %s/%s %s/%s_%s_FP.csv' % (spec_result_dir, fp_result_csv, spec_output_dir, project_id, iterator))
        parse_spec_results()
        shutil.rmtree(spec_result_dir)

        # Save SPEC results to database
        session = Session()
        try:
            session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
                Olympus.perlbench_base_copies: results['400.perlbench_base_copies'],
                Olympus.perlbench_base_runtime: results['400.perlbench_base_runtime'],
                Olympus.perlbench_base_rate: results['400.perlbench_base_rate'],
                Olympus.perlbench_peak_copies: results['400.perlbench_peak_copies'],
                Olympus.perlbench_peak_runtime: results['400.perlbench_peak_runtime'],
                Olympus.perlbench_peak_rate: results['400.perlbench_peak_rate'],
                Olympus.bzip2_base_copies: results['401.bzip2_base_copies'],
                Olympus.bzip2_base_runtime: results['401.bzip2_base_runtime'],
                Olympus.bzip2_base_rate: results['401.bzip2_base_rate'],
                Olympus.bzip2_peak_copies: results['401.bzip2_peak_copies'],
                Olympus.bzip2_peak_runtime: results['401.bzip2_peak_runtime'],
                Olympus.bzip2_peak_rate: results['401.bzip2_peak_rate'],
                Olympus.gcc_base_copies: results['403.gcc_base_copies'],
                Olympus.gcc_base_runtime: results['403.gcc_base_runtime'],
                Olympus.gcc_base_rate: results['403.gcc_base_rate'],
                Olympus.gcc_peak_copies: results['403.gcc_peak_copies'],
                Olympus.gcc_peak_runtime: results['403.gcc_peak_runtime'],
                Olympus.gcc_peak_rate: results['403.gcc_peak_rate'],
                Olympus.mcf_base_copies: results['429.mcf_base_copies'],
                Olympus.mcf_base_runtime: results['429.mcf_base_runtime'],
                Olympus.mcf_base_rate: results['429.mcf_base_rate'],
                Olympus.mcf_peak_copies: results['429.mcf_peak_copies'],
                Olympus.mcf_peak_runtime: results['429.mcf_peak_runtime'],
                Olympus.mcf_peak_rate: results['429.mcf_peak_rate'],
                Olympus.xalancbmk_base_copies: results['483.xalancbmk_base_copies'],
                Olympus.xalancbmk_base_runtime: results['483.xalancbmk_base_runtime'],
                Olympus.xalancbmk_base_rate: results['483.xalancbmk_base_rate'],
                Olympus.xalancbmk_peak_copies: results['483.xalancbmk_peak_copies'],
                Olympus.xalancbmk_peak_runtime: results['483.xalancbmk_peak_runtime'],
                Olympus.xalancbmk_peak_rate: results['483.xalancbmk_peak_rate'],
                Olympus.soplex_base_copies: results['450.soplex_base_copies'],
                Olympus.soplex_base_runtime: results['450.soplex_base_runtime'],
                Olympus.soplex_base_rate: results['450.soplex_base_rate'],
                Olympus.soplex_peak_copies: results['450.soplex_peak_copies'],
                Olympus.soplex_peak_runtime: results['450.soplex_peak_runtime'],
                Olympus.soplex_peak_rate: results['450.soplex_peak_rate'],
                Olympus.sphinx3_base_copies: results['482.sphinx3_base_copies'],
                Olympus.sphinx3_base_runtime: results['482.sphinx3_base_runtime'],
                Olympus.sphinx3_base_rate: results['482.sphinx3_base_rate'],
                Olympus.sphinx3_peak_copies: results['482.sphinx3_peak_copies'],
                Olympus.sphinx3_peak_runtime: results['482.sphinx3_peak_runtime'],
                Olympus.sphinx3_peak_rate: results['482.sphinx3_peak_rate']
            })
            session.commit()
            print "\n------ Completed SPEC ------"
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    print "\nIteration %s completed\n" % iterator

    iterator += 1
    sleep(sleeptime)  # Any delay before the next round is executed

# Remove Geekbench dist folder
os.chdir(BASE_DIR)
shutil.rmtree('dist')

print "----------------------------------------------------------------------------------"
print " All tests are successfully completed and the results are transferred to database "
print "----------------------------------------------------------------------------------"
