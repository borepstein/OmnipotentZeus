#To-do list:
#Soon: Do the same for iperf

import json
import os
import csv
import subprocess as sub
from time import sleep, time
from collections import OrderedDict as od
from prometheus_azure import Base, Olympus, Hermes_System, HermesRand, HermesSeq, HermesNet
from prometheus_azure import Ignition
from sqlalchemy.orm import sessionmaker
from random import randint

#Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
DBSession          = sessionmaker(bind=Ignition)
session            = DBSession()

#Variables for Geekbench: Email and Key for unlocking the license
email   = 'contact@cloudspectator.com'
key     = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'

#Variables for the OS: the Geekbench Directory
directory   = "dist/Geekbench-3.1.2-Linux"

#====================GLOBAL INTRODUCTION====================#
os.system('clear')
print "|------------------------|"
print "|    Project Olympus     |"
print "|         v1.0           |"
print "|------------------------|"
print ""
print "Project Olympus is designed to be a testbed for measuring virtual machine performance in a scalable, cloud environment. The design of Olympus is its flexibility in continuous testing over time, rather than spot testing, which is an archaic method that cannot apply to highly variable environments with multiple (many of which are possibly uncontrolled) variables."
print ""
print ""

#====================GLOBAL INSTALLER====================#
#Check to see if all programs are installed
sleep(1)
print "Please enter the Project ID. All tests that are categorized under the same project ID will be associated. This makes data collection and analysis easier. The format for the project ID is as follows:\n"
print "x-name-startdate\n"
print "- For x, please state whether it is commissioned (with the letter c) or internal (with the letter i)."
print "- For the name, if it is commissioned, please enter the commissioner's name (e.g., 1and1). If it is internal, please name the project."
print "- For the start date, please enter the YYYYMMDD input for when the tests FIRST started (e.g., 20150424)"
print "- SAMPLE ID: c-1and1-20150424 (Commissioned 1and1 report that started on 2015-04-24)"
print "\n\n\n"
project_input = "test"
print "\n\n"
print "Before we begin, we need to install the baseline tests to run the Hermes suite. The proper tests must always be installed."
print ""
global_install = raw_input("Do you need to install the test programs (y/n)? ")

#IF yes, then need to install the tests
if global_install == 'y':
    #Install fio for disk testing
    os.system('apt-get install fio --yes')
    #Install screen
    os.system('apt-get install screen')
    #Install iperf for network testing
    os.system('apt-get install iperf')
    #Install Geekbench - Licensing Information
    email   = 'contact@cloudspectator.com'
    key     = 'tqw3g-d4myf-mqy2u-zifzg-wzidc-yo7mp-dulwf-5zsu7-yggfs'
    #Install Geekbench - Download & Unpackage
    os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz")
    os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
    os.chdir('dist/Geekbench-3.1.2-Linux')
    sub.call(['./geekbench_x86_64','-r',email,key])
else: 
    print "You have opted to skip the install. All tests must be installed in order for this program to run correctly."
    os.chdir('dist/Geekbench-3.1.2-Linux')

#====================GLOBAL VARIABLES====================#
#Timer for between runs (sleeptime), and how many total runs (iterations)
print ""
print "|------------------------|"
print "|    GLOBAL VARIABLES    |"
print "|------------------------|"
print ""
sleeptime       = 0
iterations      = 20000
duration        = 24 * 86400

#Collect information on the provider and VM environment
provider_input   = "interoute"
provider_region  = "london"
startdate_input  = raw_input("Please enter the start date for this test in YYYYMMDD (e.g., 20150115 for January 15TH, 2015): ")
vm_input         = raw_input("Please enter the VM name (if no VM name, just say vCPU/RAM in GB (e.g., 2vCPU/4GB): ")
vm_input         = vm_input.lower()
vmcount_input    = raw_input("If this is a VM in a series of same-size VMs on the same provider, please give this VM a unique number (e.g., 1 for first one you are provisioning): ")
vcpu_input       = raw_input("vCPU(s): ")
ram_input        = raw_input("RAM (in GB): ")
local_input      = raw_input("Local Disk (in GB). Put 0 if none: ")
block_input      = raw_input("Block Disk (in GB). Put 0 if none: ")

#Generate a random number to add to the unique ID for this provider and VM combination in the test cycle
random_uid    = randint(0,1000000)
generated_uid = provider_input + vm_input + startdate_input + str(random_uid)

#Check which test categories to run
system_tests = "y"

disk_rand = "y"

disk_seq = "y"

internal_net_tests = "y"

if disk_rand == 'y'or disk_seq == 'y':
    print ""
    print "|---------------------------|"
    print "|    DISK TEST VARIABLES    |"
    print "|---------------------------|"
    print ""
    fio_blocksize = "8"
    fio_blocksize = '-bs=' + fio_blocksize + 'k'
    fio_filesize = "200"
    fio_filesize = '-size=' + fio_filesize + "M"
    fio_numjobs = "5"
    spider_hatchlings = int(fio_numjobs) + 1
    fio_numjobs = '-numjobs=' + fio_numjobs
    fio_runtime = "60"
    fio_runtime = '-runtime=' + fio_runtime

    fio_json_file = 'fio.json'
    fio_filename = '-name=spider_eggs'

    fio_direct = "y"
    if fio_direct == 'y':
        fio_direct_val = "Direct"
        fio_direct = '-direct=1'
    else:
        fio_direct_val = "Cached"
        fio_direct = '-direct=0'

if disk_rand =='y':
    fio_rand_rw = '-rw=randrw'

if disk_seq =='y':
    fio_seq_rw = '-rw=rw'

if internal_net_tests == 'y':
    print ""
    print "|---------------------------------------|"
    print "|    INTERNAL NETWORK TEST VARIABLES    |"
    print "|---------------------------------------|"
    print ""
    internal_net_ip = raw_input('Please enter the IP address of the server you are trying to connect to: ')
    internal_net_time = "60"
    #TEST
    #internal_net_ip = "104.236.16.20"
    #internal_net_time = "20"
    internal_net_csv = "C"

#====================GLOBAL TESTING====================#
iterator = 1
start = time()
for x in range(iterations):
    stop = time() - start
    if stop >= duration:
        break
    if system_tests == 'y':
        #Run Geekbench
        sub.call(['./geekbench_x86_64','--no-upload','--export-json','geekbench.json'])

        #OPEN the file
        geekbench_json = open('geekbench.json')

        #Load the JSON file
        data = json.load(geekbench_json)

        #Parse the Variables
        #Integer multi-core numbers
        y = 0
        scores = {}
        for x in range(0,13,1):
            z           = str(data['sections'][0]['workloads'][y]['name'])
            scores[z]   = str(data['sections'][0]['workloads'][y]['results'][1]['rate_string'])
            y           = y + 1
        y = 0
        for x in range(0,10,1):
            z           = str(data['sections'][1]['workloads'][y]['name'])
            scores[z]   = str(data['sections'][1]['workloads'][y]['results'][1]['rate_string'])
            y           = y + 1
        y = 0
        for x in range(0,4,1):
            z           = str(data['sections'][2]['workloads'][y]['name'])
            scores[z]   = str(data['sections'][2]['workloads'][y]['results'][1]['rate_string'])
            y           = y + 1
        y = 0
        for x in range(0,3,1):
            z           = str(data['sections'][y]['name'])+" Multicore"
            scores[z]   = str(data['sections'][y]['multicore_score'])
            y           = y + 1
        y = 0
        for x in range(0,1):
            z           = "Total"
            scores[z]   = str(data['multicore_score'])
            y           = y + 1
        for x in range(0,1):
            z           = "Runtime"
            scores[z]   = str(data['runtime'])
        
        scores = od(scores)
        y = 0
        values = {}
        for key,val in scores.items():
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
        os.remove('geekbench.json')
        print "removed GB"
        #Close the Geekbench file when you're done with it
        geekbench_json.close()
        print "Closed GB JSON."

    #Run Disk Tests if disk tests are enabled   
    if disk_rand == 'y':
        #fio -rw=readwrite -name fio_testfile -bs=8k -size=1024M -numjobs=16 -runtime=60 -direct=1 -time_based -group_reporting -exitall
        sub.call(['fio',fio_rand_rw,fio_filename,fio_blocksize,fio_filesize,fio_numjobs,fio_runtime,fio_direct,'-time_based','--output-format=json','--output=fio.json','-time_based' ,'-group_reporting','-exitall'])

        #OPEN the file
        fio_json = open(fio_json_file)

        #Load the JSON file
        fio_data = json.load(fio_json)

        runtime_read_rand  = str(fio_data['jobs'][0]        ['read']           ['runtime'])
        runtime_write_rand = str(fio_data['jobs'][0]        ['write']          ['runtime'])
        ops_read_rand      = str(fio_data['disk_util'][0]   ['read_ios'])
        ops_write_rand     = str(fio_data['disk_util'][0]   ['write_ios'])
        io_read_rand       = str(fio_data['jobs'][0]        ['read']           ['io_bytes'])
        io_write_rand      = str(fio_data['jobs'][0]        ['write']          ['io_bytes'])
        iops_read_rand     = str(fio_data['jobs'][0]        ['read']           ['iops'])
        iops_write_rand    = str(fio_data['jobs'][0]        ['write']          ['iops'])
        bw_read_rand       = str(fio_data['jobs'][0]        ['read']           ['bw'])
        bw_write_rand      = str(fio_data['jobs'][0]        ['write']          ['bw'])
        ticks_read_rand    = str(fio_data['disk_util'][0]   ['read_ticks'])
        ticks_write_rand   = str(fio_data['disk_util'][0]   ['write_ticks'])
        fio_json.close()
        os.remove(fio_json_file)
        #Remove the spider eggs I laid.
        for baby_spiders in range(1,spider_hatchlings):
            spideregg_file = "spider_eggs." + str(baby_spiders) + ".0"
            os.remove(spideregg_file)

    if disk_seq =='y':
        #fio -rw=readwrite -name fio_testfile -bs=8k -size=1024M -numjobs=16 -runtime=60 -direct=1 -time_based -group_reporting -exitall
        sub.call(['fio',fio_seq_rw,fio_filename,fio_blocksize,fio_filesize,fio_numjobs,fio_runtime,fio_direct,'-time_based','--output-format=json','--output=fio.json','-time_based' ,'-group_reporting','-exitall'])

        #OPEN the file
        fio_json = open(fio_json_file)

        #Load the JSON file
        fio_data = json.load(fio_json)

        runtime_read_seq  = str(fio_data['jobs'][0]        ['read']           ['runtime'])
        runtime_write_seq = str(fio_data['jobs'][0]        ['write']          ['runtime'])
        ops_read_seq      = str(fio_data['disk_util'][0]   ['read_ios'])
        ops_write_seq     = str(fio_data['disk_util'][0]   ['write_ios'])
        io_read_seq       = str(fio_data['jobs'][0]        ['read']           ['io_bytes'])
        io_write_seq      = str(fio_data['jobs'][0]        ['write']          ['io_bytes'])
        iops_read_seq     = str(fio_data['jobs'][0]        ['read']           ['iops'])
        iops_write_seq    = str(fio_data['jobs'][0]        ['write']          ['iops'])
        bw_read_seq       = str(fio_data['jobs'][0]        ['read']           ['bw'])
        bw_write_seq      = str(fio_data['jobs'][0]        ['write']          ['bw'])
        ticks_read_seq    = str(fio_data['disk_util'][0]   ['read_ticks'])
        ticks_write_seq   = str(fio_data['disk_util'][0]   ['write_ticks'])
        fio_json.close()
        os.remove(fio_json_file)
        #Remove the spider eggs I laid.
        for baby_spiders in range(1,spider_hatchlings):
            spideregg_file = "spider_eggs." + str(baby_spiders) + ".0"
            os.remove(spideregg_file)

    if internal_net_tests == 'y':
        #iperf -c IP_ADDRESS -t TIME -f m -y C >> iperf_results.csv
        sub.call(['iperf','-c',internal_net_ip,'-t',internal_net_time,'-y',internal_net_csv],stdout=open("iperf_results.csv","w"))

        internal_net_csv_file = 'iperf_results.csv'
        opener = open(internal_net_csv_file)
        csv_open = csv.reader(opener)
        for row in csv_open:
            internal_network_data = int(row[7])
            internal_network_data = (internal_network_data / 1024) / 1024
            print internal_network_data
            internal_network_bandwidth = int(row[8])
            internal_network_bandwidth = (internal_network_bandwidth / 1024) / 1024
            print internal_network_bandwidth
        print "finished transferring"
        os.remove(internal_net_csv_file)
        print "finished deleting the file"

#====================GLOBAL TRANSMITTING====================#
    #Transmit data back to Olympuss
    print "Transmitting to Olympus"
    if iterator == 1:
        print "Transfer..."
        Open_Olympus       = Olympus(
            project        = project_input,
            provider       = provider_input,
            region         = provider_region,
            startdate      = startdate_input,
            uid            = generated_uid,
            vm             = vm_input,
            vmcount        = vmcount_input,
            vcpu           = vcpu_input,
            ram            = ram_input,
            local          = local_input,
            block          = block_input,
            disk_rand      = "both",
            disk_seq       = "both",
            disk_blocksize = "8kb",
            disk_filesize  = "200mb",
            disk_numjobs   = "5",
            disk_direct    = "Direct")
        print "Transfer 1"
        session.add(Open_Olympus)
        print "Transfer 2"

    #Parse data into System Results if processor & memory tests were requested
    print "Transmit 2"
    if system_tests == 'y':
        print "Transmit system"
        Hermes_System_Results   = Hermes_System(
            uid                 = generated_uid,
            iteration           = iterator,
            runtime             = values['Runtime'],
            intmulti            = values['Integer Multicore'],
            floatmulti          = values['Floating Point Multicore'],
            memmulti            = values['Memory Multicore'],
            totalmulti          = values['Total'],
            aes                 = values['AES'],
            twofish             = values['Twofish'],
            sha1                = values['SHA1'],
            sha2                = values['SHA2'],
            bzipcompression     = values['BZip2 Compress'],
            bzipdecompression   = values['BZip2 Decompress'],
            jpegcompression     = values['JPEG Compress'],
            jpegdecompression   = values['JPEG Decompress'],
            pngcompression      = values['PNG Compress'],
            pngdecompression    = values['PNG Decompress'],
            sobel               = values['Sobel'],
            lua                 = values['Lua'],
            dijkstra            = values['Dijkstra'],
            blackscholes        = values['BlackScholes'],
            mandelbrot          = values['Mandelbrot'],
            sharpenimage        = values['Sharpen Filter'],
            blurimage           = values['Blur Filter'],
            sgemm               = values['SGEMM'],
            dgemm               = values['DGEMM'],
            sfft                = values['SFFT'],
            dfft                = values['DFFT'],
            nbody               = values['N-Body'],
            raytrace            = values['Ray Trace'],
            copy                = values['Stream Copy'],
            scale               = values['Stream Scale'],
            add                 = values['Stream Add'],
            triad               = values['Stream Triad'])
        session.add(Hermes_System_Results)
        print "Added session"
        #Remove the geekbench file

    #parse data into Disk Results if disk tests were requested
    if disk_rand == 'y':
        print "add Rand Disk"
        Hermes_Rand             = HermesRand(
            uid                 = generated_uid,
            iteration           = iterator,
            read_runtime        = runtime_read_rand,
            write_runtime       = runtime_write_rand,
            read_iops           = iops_read_rand,
            read_io             = io_read_rand,
            read_bw             = bw_read_rand,
            read_ticks          = ticks_read_rand,
            write_iops          = iops_write_rand,
            write_io            = io_write_rand,
            write_bw            = bw_write_rand,
            write_ticks         = ticks_write_rand)
        session.add(Hermes_Rand)
        print "added Rand Disk"

    if disk_seq == 'y':
        print "add Seq Disk"
        Hermes_Seq              = HermesSeq(
            uid                 = generated_uid,
            iteration           = iterator,
            read_runtime        = runtime_read_seq,
            write_runtime       = runtime_write_seq,
            read_iops           = iops_read_seq,
            read_io             = io_read_seq,
            read_bw             = bw_read_seq,
            read_ticks          = ticks_read_seq,
            write_iops          = iops_write_seq,
            write_io            = io_write_seq,
            write_bw            = bw_write_seq,
            write_ticks         = ticks_write_seq)
        session.add(Hermes_Seq)
        print "added Seq Disk"

    if internal_net_tests == 'y':
        print "add Net"
        Hermes_Net              = HermesNet(
            uid                 = generated_uid,
            iteration           = iterator,
            transfer_mb         = internal_network_data,
            bandwidth_mb        = internal_network_bandwidth)
        session.add(Hermes_Net)
        print "added Net"
        session.commit()
        print "committed All"
        session.close()
        print "Closing Session"

    iterator = iterator + 1