#TO-DO
#Add Geekbench's Processor Information to collect that into the database

#Don't forget to change this first import to import the correct configuration file
from projects.test import *
import json
import os
import csv
import subprocess as sub
import smtplib as smtp
import multiprocessing
import urllib2
import zipfile
from time import sleep, time
from bs4 import BeautifulSoup as bs
from collections import OrderedDict as od
from prometheus import Base, Olympus, Hermes_System, HermesRand, HermesSeq, HermesNet, HermesPTS
from prometheus import Ignition
from sqlalchemy.orm import sessionmaker
from random import randint
from psutil import virtual_memory

#Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
DBSession          = sessionmaker(bind=Ignition)
session            = DBSession()

#====================GLOBAL INTRODUCTION====================#
os.system('cls')
print "|------------------------|"
print "|    Project Olympus     |"
print "|         v1.5           |"
print "|------------------------|"
print ""
print "Project Olympus is designed to be a testbed for measuring virtual machine performance in a scalable, cloud environment. The design of Olympus is its flexibility in continuous testing over time, rather than spot testing, which is an archaic method that cannot apply to highly variable environments with multiple (many of which are possibly uncontrolled) variables."
print ""
print ""

processor_info = ''

if operating_system == 'windows': 
    if system_tests == 'y': #Install Geekbench - Download & Unpackage if to be tested
        if not os.path.isfile('Geekbench-3.3.2-WindowsSetup.exe'):
            os.system('wget --no-check-certificate https://s3.amazonaws.com/internal-downloads/Geekbench-3.3.2-WindowsSetup.exe')
            sub.call(['Geekbench-3.3.2-WindowsSetup.exe','-r',email,key], shell=True)
    if disk_rand == 'y' or disk_seq =='y':  #Install fio for disk testing if to be tested
        if not os.path.isfile('SQLIO.msi'):
            os.system('wget http://download.microsoft.com/download/f/3/f/f3f92f8b-b24e-4c2e-9e86-d66df1f6f83b/SQLIO.msi')
            sub.call(['SQLIO.msi'], shell=True)
    if internal_net_tests == 'y': #Install iperf for network testing if to be tested
        if not os.path.isfile('iperf-3.0.11-win64.zip'):
            os.system('wget --no-check-certificate https://iperf.fr/download/iperf_3.0/iperf-3.0.11-win64.zip')
            with zipfile.ZipFile('iperf-3.0.11-win64.zip', "r") as z:
                z.extractall()

#Getting CPU Amount
vcpu_input = multiprocessing.cpu_count()

#RAM Amount
mem = virtual_memory()
ram_input = (float(mem.total) / 1024.0 / 1024.0 / 1024.0)

#Collect information on the provider and VM environment
provider_input   = raw_input("Please enter the provider's name (Netelligent, Rackspace, AWS , SunGard , Peak10, Dimension Data or Azure): ")
provider_input   = provider_input.lower()
while True:
    if provider_input == 'netelligent':
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
        provider_input   = raw_input("Please enter the provider's name (No spaces; e.g., 'Digital Ocean' should be 'digitalocean'): ")
        provider_input   = provider_input.lower()

vm_input         = raw_input("Please enter the VM name (if no VM name, just say vCPU/RAM in GB (e.g., 2vCPU/4GB): ")
vm_input         = vm_input.lower()
vmcount_input    = '0'
local_input      = raw_input("Local Disk (in GB). Put 0 if none: ")
block_input      = raw_input("Block Disk (in GB). Put 0 if none: ")

#Generate a random number to add to the unique ID for this provider and VM combination in the test cycle
random_uid    = randint(0, 1000000)
generated_uid = provider_input + vm_input + startdate_input + str(random_uid)

if internal_net_tests == 'y':
    internal_net_ip = raw_input('Please enter the IP address of the server you are trying to connect to: ')
    internal_net_csv = "C"

#====================GLOBAL TESTING====================#

if system_tests == 'y':
    #Run Geekbench
    #sub.call(['./geekbench_x86_64','--no-upload','--export-json', 'gb.json'])
    sub.call(['C:\Program Files (x86)\Geekbench 3\geekbench_x86_64.exe','--no-upload','--export-json', 'gb.json'], shell=True)
    
    #OPEN the file
    geekbench_json = open('gb.json')

    #Load the JSON file
    data = json.load(geekbench_json)
    processor_info = str(data['metrics'][6]['value'])

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
    for x in range(0,3,1):
        z           = str(data['sections'][y]['name'])+" Singlecore"
        scores[z]   = str(data['sections'][y]['score'])
        y           = y + 1
    y = 0
    for x in range(0,1):
        z           = "Total"
        scores[z]   = str(data['multicore_score'])
        y           = y + 1
    for x in range(0,1):
        z           = "Total Single"
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

if disk_rand == 'y':
    output_file = 'diskrand.txt'

    sub.call(['C:\Program Files (x86)\SQLIO\sqlio.exe', '-kR', '-s10', '-frandom', '-b8'], stdout=open(output_file, "w"))
    for row in open(output_file):
        line = row.rstrip()
        if "IOs/sec" in line:
            item = line.split(":")
            read_iops_rand = float(item[1].strip())
            break

    for row in open(output_file):
        line = row.rstrip()
        if "MBs/sec" in line:
            item = line.split(":")
            read_mbps_rand = float(item[1].strip())
            break

    sub.call(['C:\Program Files (x86)\SQLIO\sqlio.exe', '-kW', '-s10', '-frandom', '-b8'], stdout=open(output_file, "w"))
    for row in open(output_file):
        line = row.rstrip()
        if "IOs/sec" in line:
            item = line.split(":")
            write_iops_rand = float(item[1].strip())
            break

    for row in open(output_file):
        line = row.rstrip()
        if "MBs/sec" in line:
            item = line.split(":")
            write_mbps_rand = float(item[1].strip())
            break

    print "finished transferring"
    os.remove(output_file)
    print "finished deleting the file"

if disk_seq == 'y':
    output_file = 'diskseq.txt'

    sub.call(['C:\Program Files (x86)\SQLIO\sqlio.exe', '-kR', '-s10', '-fsequential', '-b64'], stdout=open(output_file, "w"))
    for row in open(output_file):
        line = row.rstrip()
        if "IOs/sec" in line:
            item = line.split(":")
            read_iops_seq = float(item[1].strip())
            break

    for row in open(output_file):
        line = row.rstrip()
        if "MBs/sec" in line:
            item = line.split(":")
            read_mbps_seq = float(item[1].strip())
            break

    sub.call(['C:\Program Files (x86)\SQLIO\sqlio.exe', '-kW', '-s10', '-fsequential', '-b64'], stdout=open(output_file, "w"))
    for row in open(output_file):
        line = row.rstrip()
        if "IOs/sec" in line:
            item = line.split(":")
            write_iops_seq = float(item[1].strip())
            break

    for row in open(output_file):
        line = row.rstrip()
        if "MBs/sec" in line:
            item = line.split(":")
            write_mbps_seq = float(item[1].strip())
            break

    print "finished transferring"
    os.remove(output_file)
    print "finished deleting the file"

if internal_net_tests == 'y':
    # iperf -c IP_ADDRESS -t TIME -f m -y C >> iperf_results.csv
    sub.call(['iperf3.exe', '-c', internal_net_ip, '-t', internal_net_time, '-y', 'C'], stdout=open("iperf_results.csv","w"))

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
#Transmit data back to Olympus
print "Transmitting to Olympus"
print "Transfer..."
Open_Olympus       = Olympus(
    project        = project_id,
    provider       = provider_input,
    region         = provider_region,
    startdate      = startdate_input,
    processor      = processor_info,
    uid            = generated_uid,
    vm             = vm_input,
    vmcount        = vmcount_input,
    vcpu           = vcpu_input,
    ram            = ram_input,
    local          = local_input,
    block          = block_input)
print "Transfer 1"
session.add(Open_Olympus)
print "Transfer 2"
session.commit()
print "Transfer Complete"

#Parse data into System Results if processor & memory tests were requested
if system_tests == 'y':
    Hermes_System_Results   = Hermes_System(
        uid                 = generated_uid,
        runtime             = values['Runtime'],
        intmulti            = values['Integer Multicore'],
        floatmulti          = values['Floating Point Multicore'],
        memmulti            = values['Memory Multicore'],
        intsingle           = values['Integer Singlecore'],
        floatsingle         = values['Floating Point Singlecore'],
        memsingle           = values['Memory Singlecore'],
        totalmulti          = values['Total'],
        totalsingle         = values['Total Single'],
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
    session.commit()
    #Remove the geekbench file
    #os.remove('gb.json')
    #Close the Geekbench file when you're done with it
    geekbench_json.close()

#parse data into Disk Results if disk tests were requested
if disk_rand == 'y':
    Hermes_Rand             = HermesRand(
        uid                 = generated_uid,
        write_mbps_rand     = write_mbps_rand,
        read_mbps_rand      = read_mbps_rand,
        write_iops_rand     = write_iops_rand,
        read_iops_rand      = read_iops_rand)
    session.add(Hermes_Rand)
    session.commit()

if disk_seq == 'y':
    Hermes_Seq              = HermesSeq(
        uid                 = generated_uid,
        write_mbps_seq      = write_mbps_seq,
        read_mbps_seq       = read_mbps_seq,
        write_iops_seq      = write_iops_seq,
        read_iops_seq       = read_iops_seq)
    session.add(Hermes_Seq)
    session.commit()

if internal_net_tests == 'y':
    Hermes_Net              = HermesNet(
        uid                 = generated_uid,
        transfer_mb         = internal_network_data,
        bandwidth_mb        = internal_network_bandwidth)
    session.add(Hermes_Net)
    session.commit()

if textnotifications == 'y':
    try:
        server = smtp.SMTP("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.login(smtp_username,smtp_password)
        message = tester_name + ", the testing on your " + provider_input + " VM (" + vm_input + ") is completed."
        FROM = 'Hermestxtnotifications@gmail.com'
        server.sendmail(FROM, TO, message)
        server.close()
        print "Text Sent"
    except:
        print "Not sent"
