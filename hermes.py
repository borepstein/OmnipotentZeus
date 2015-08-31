from projects.test import *
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
os.system('cls')
print "|------------------------|"
print "|    Project Olympus     |"
print "|         v1.5           |"
print "|------------------------|"
print ""
print "Project Olympus is designed to be a testbed for measuring virtual machine performance in a scalable, cloud environment. The design of Olympus is its flexibility in continuous testing over time, rather than spot testing, which is an archaic method that cannot apply to highly variable environments with multiple (many of which are possibly uncontrolled) variables."
print ""
print ""

# Download executable files for running tests
if operating_system == 'windows':
    if system_tests == 'y':  # Install Geekbench - Download & Unpackage if to be tested
        if not os.path.isfile('Geekbench-3.3.2-WindowsSetup.exe'):
            os.system('wget --no-check-certificate https://s3.amazonaws.com/internal-downloads/Geekbench-3.3.2-WindowsSetup.exe')
            sub.call(['Geekbench-3.3.2-WindowsSetup.exe', '-r', email, key], shell=True)
    if disk_rand == 'y' or disk_seq == 'y':  # Install fio for disk testing if to be tested
        if not os.path.isfile('SQLIO.msi'):
            os.system('wget http://download.microsoft.com/download/f/3/f/f3f92f8b-b24e-4c2e-9e86-d66df1f6f83b/SQLIO.msi')
            sub.call(['SQLIO.msi'], shell=True)
    if internal_net_tests == 'y':  # Install iperf for network testing if to be tested
        if not os.path.isfile('iperf3.exe'):
            os.system('wget --no-check-certificate https://iperf.fr/download/iperf_3.0/iperf-3.0.11-win64.zip')
            with zipfile.ZipFile('iperf-3.0.11-win64.zip', "r") as z:
                z.extractall()
            os.remove('iperf-3.0.11-win64.zip')

# Fetching CPU Amount
vcpu_input = multiprocessing.cpu_count()

# Fetching RAM Amount
mem = virtual_memory()
ram_input = "%.2f" % (float(mem.total) / 1024.0 / 1024.0 / 1024.0)

# Collect information on the provider and VM environment
provider_input = raw_input("Please enter the provider's name (Netelligent, Rackspace, AWS , SunGard , Peak10, Dimension Data or Azure): ")
provider_input = provider_input.lower()
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
        provider_input = raw_input("Please enter the provider's name (No spaces; e.g., 'Digital Ocean' should be 'digitalocean'): ")
        provider_input = provider_input.lower()

vm_input = raw_input("Please enter the VM name (if no VM name, just say vCPU/RAM in GB (e.g., 2vCPU/4GB): ")
vm_input = vm_input.lower()
vmcount_input = '0'
local_input = raw_input("Local Disk (in GB). Put 0 if none: ")
block_input = raw_input("Block Disk (in GB). Put 0 if none: ")

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

    if system_tests == 'y':

        # Run Geekbench
        geekbench_output = 'gb.json'
        sub.call([geekbench_install_dir + '\Geekbench 3\geekbench_x86_64.exe', '--no-upload','--export-json', geekbench_output], shell=True)

        # Parse variables from Geekbench result

        geekbench_file_handler = open(geekbench_output)
        data = json.load(geekbench_file_handler)
        processor_info = str(data['metrics'][6]['value'])

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

    if disk_rand == 'y':

        sqlio_output = 'sqlio_results.txt'

        # Run disk random test for 'write'
        sub.call([sqlio_install_dir + '\SQLIO\sqlio.exe', '-kW', '-s10', '-frandom', '-b4'], stdout=open(sqlio_output, "w"))

        # Parse variables from disk random write result
        sqlio_file_handler = open(sqlio_output)
        for row in sqlio_file_handler:
            line = row.rstrip()
            if "IOs/sec" in line:
                item = line.split(":")
                write_iops_rand = float(item[1].strip())
                break

        for row in sqlio_file_handler:
            line = row.rstrip()
            if "MBs/sec" in line:
                item = line.split(":")
                write_mbps_rand = float(item[1].strip())
                break

        sqlio_file_handler.close()

        # Run disk random test for 'read'
        sub.call([sqlio_install_dir + '\SQLIO\sqlio.exe', '-kR', '-s10', '-frandom', '-b4'], stdout=open(sqlio_output, "w"))

        # Parse variables from disk random read result
        sqlio_file_handler = open(sqlio_output)
        for row in sqlio_file_handler:
            line = row.rstrip()
            if "IOs/sec" in line:
                item = line.split(":")
                read_iops_rand = float(item[1].strip())
                break

        for row in sqlio_file_handler:
            line = row.rstrip()
            if "MBs/sec" in line:
                item = line.split(":")
                read_mbps_rand = float(item[1].strip())
                break

        sqlio_file_handler.close()
        print "Completed disk random tests"

    if disk_seq == 'y':

        sqlio_output = 'sqlio_results.txt'

        # Run disk sequential test for 'write'
        sub.call([sqlio_install_dir + '\SQLIO\sqlio.exe', '-kW', '-s10', '-fsequential', '-b4'], stdout=open(sqlio_output, "w"))

        # Parse variables from disk sequential write result
        sqlio_file_handler = open(sqlio_output)
        for row in sqlio_file_handler:
            line = row.rstrip()
            if "IOs/sec" in line:
                item = line.split(":")
                write_iops_seq = float(item[1].strip())
                break

        for row in sqlio_file_handler:
            line = row.rstrip()
            if "MBs/sec" in line:
                item = line.split(":")
                write_mbps_seq = float(item[1].strip())
                break

        sqlio_file_handler.close()

        # Run disk sequential test for 'read'
        sub.call([sqlio_install_dir + '\SQLIO\sqlio.exe', '-kR', '-s10', '-fsequential', '-b4'], stdout=open(sqlio_output, "w"))

        # Parse variables from disk sequential read result
        sqlio_file_handler = open(sqlio_output)
        for row in sqlio_file_handler:
            line = row.rstrip()
            if "IOs/sec" in line:
                item = line.split(":")
                read_iops_seq = float(item[1].strip())
                break

        for row in sqlio_file_handler:
            line = row.rstrip()
            if "MBs/sec" in line:
                item = line.split(":")
                read_mbps_seq = float(item[1].strip())
                break

        sqlio_file_handler.close()
        print "Completed disk sequential tests"

    if disk_rand == 'y' or disk_seq == 'y':
        # Remove output file generated during SQLIO test
        if os.path.isfile(sqlio_output):
            os.remove(sqlio_output)

    if internal_net_tests == 'y':

        # Run iperf test
        iperf_output = 'iperf_results.txt'
        os.system("start cmd /c iperf3.exe -s")
        sub.call(['iperf3.exe', '-c', internal_net_ip], stdout=open(iperf_output, "w"))

        # Parse variables from iperf result
        output_file_handler = open(iperf_output)
        for row in output_file_handler:
            line = row.rstrip()
            if "sender" in line:
                item = line.split(" ")
                for i in range(0, len(item)):
                    if "Bytes" in item[i].strip():
                        sender_transfer_mb = float(item[i - 1].strip())
                    if "bits/sec" in item[i].strip():
                        sender_bandwidth_mb = float(item[i - 1].strip())
                break

        for row in output_file_handler:
            line = row.rstrip()
            if "receiver" in line:
                item = line.split(" ")
                for i in range(0, len(item)):
                    if "Bytes" in item[i].strip():
                        receiver_transfer_mb = float(item[i - 1].strip())
                    if "bits/sec" in item[i].strip():
                        receiver_bandwidth_mb = float(item[i - 1].strip())
                break

        output_file_handler.close()
        os.remove(iperf_output)
        print "Completed internal network tests"

    # ====================GLOBAL TRANSMITTING==================== #
    # Transmit data back to Olympus
    print "\n\n"
    print "Transmitting to Olympus"
    print "\n\n"
    Open_Olympus = Olympus(
        project=project_id,
        provider=provider_input,
        region=provider_region,
        startdate=startdate_input,
        iteration=iterator,
        uid=generated_uid,
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
            Olympus.read_mbps_rand: read_mbps_rand,
            Olympus.write_mbps_rand: write_mbps_rand,
            Olympus.read_iops_rand: read_iops_rand,
            Olympus.write_iops_rand: write_iops_rand
        })
        session.commit()
        print "Finished transferring disk random results"

    if disk_seq == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.read_mbps_seq: read_mbps_seq,
            Olympus.write_mbps_seq: write_mbps_seq,
            Olympus.read_iops_seq: read_iops_seq,
            Olympus.write_iops_seq: write_iops_seq
        })
        session.commit()
        print "Finished transferring disk sequential results"

    if internal_net_tests == 'y':

        session.query(Olympus).filter(Olympus.id == Open_Olympus.id).update({
            Olympus.sender_transfer_mb: sender_transfer_mb,
            Olympus.sender_bandwidth_mb: sender_bandwidth_mb,
            Olympus.receiver_transfer_mb: receiver_transfer_mb,
            Olympus.receiver_bandwidth_mb: receiver_bandwidth_mb
        })
        session.commit()
        print "Finished transferring internal network test results"

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
