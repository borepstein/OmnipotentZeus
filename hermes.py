#TO-DO
#Add Geekbench's Processor Information to collect that into the database

#Don't forget to change this first import to import the correct configuration file
from projects.test import *
import json
import os
import csv
import subprocess as sub
import smtplib as smtp
from time import sleep, time
from bs4 import BeautifulSoup as bs
from collections import OrderedDict as od
from prometheus import Base, Olympus, Hermes_System, HermesRand, HermesRandasync, HermesSeq, HermesSeqasync, HermesNet, HermesPTS
from prometheus import Ignition
from sqlalchemy.orm import sessionmaker
from random import randint

#Bind Ignition to the metadata of the Base class
Base.metadata.bind = Ignition
DBSession          = sessionmaker(bind=Ignition)
session            = DBSession()

#====================GLOBAL INTRODUCTION====================#
os.system('clear')
print "|------------------------|"
print "|    Project Olympus     |"
print "|         v1.5           |"
print "|------------------------|"
print ""
print "Project Olympus is designed to be a testbed for measuring virtual machine performance in a scalable, cloud environment. The design of Olympus is its flexibility in continuous testing over time, rather than spot testing, which is an archaic method that cannot apply to highly variable environments with multiple (many of which are possibly uncontrolled) variables."
print ""
print ""

#====================GLOBAL INSTALLER====================#
if operating_system =='centos' or operating_system == 'redhat':
    if disk_rand == 'y' or disk_seq == 'y': #Install fio for disk testing if to be tested
        os.system('wget http://pkgs.repoforge.org/fio/fio-2.1.10-1.el6.rf.x86_64.rpm')
        os.system('rpm -iv fio-2.1.10-1.el6.rf.x86_64.rpm')
    if internal_net_tests == 'y': #Install iperf for network testing if to be tested
        os.system('yum install iperf -y')
    if system_tests == 'y': #Install Geekbench - Download & Unpackage if to be tested
        os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz")
        os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
        os.chdir('dist/Geekbench-3.1.2-Linux')
        sub.call(['./geekbench_x86_64','-r',email,key])

if operating_system == 'ubuntu' or operating_system == 'debian': 
    if disk_rand == 'y' or disk_seq =='y':  #Install fio for disk testing if to be tested
        os.system('apt-get install fio --yes')
    if internal_net_tests == 'y': #Install iperf for network testing if to be tested
        os.system('apt-get install iperf') 
    if system_tests == 'y': #Install Geekbench - Download & Unpackage if to be tested
        os.system("wget http://geekbench.s3.amazonaws.com/Geekbench-3.1.2-Linux.tar.gz") 
        os.system("tar -xvzf Geekbench-3.1.2-Linux.tar.gz")
        os.chdir('dist/Geekbench-3.1.2-Linux')
        sub.call(['./geekbench_x86_64','-r',email,key])
    if pts_tests == 'y': #Install Phoronix if to be tested
        os.system('apt-get install phoronix-test-suite --yes')
        os.system('y | phoronix-test-suite')
        os.system('mv ~/OmnipotentZeus/user-config.xml ~/.phoronix-test-suite/user-config.xml')

#Getting CPU Amount
v1               = sub.Popen(['cat','/proc/cpuinfo'],stdout=sub.PIPE)
v2               = sub.Popen(['grep','processor'], stdin=v1.stdout, stdout=sub.PIPE)
v3               = sub.Popen(['wc','-l'], stdin=v2.stdout, stdout=sub.PIPE)
vcpu_input       = v3.communicate()[0]
#RAM Amount
r1 = sub.Popen(['cat','/proc/meminfo'],stdout=sub.PIPE)
r2 = sub.Popen(['grep','MemTotal'], stdin=r1.stdout, stdout=sub.PIPE)
memoutput        = r2.communicate()[0]
memoutput_list   = memoutput.split(' ')
for x in memoutput_list:
    if x.isalnum(): #Converting from bytes to GB
        mem_count = int(x)
        mem_count = (mem_count / 1024.0 / 1024.0)
        ram_input = "%.2f" % mem_count

#Collect information on the provider and VM environment
provider_input   = raw_input("Please enter the provider's name: ")
provider_input   = provider_input.lower()
provider_region  = "N/A"

vm_input         = raw_input("Please enter the VM name (if no VM name, just say vCPU/RAM in GB (e.g., 2vCPU/4GB): ")
vm_input         = vm_input.lower()
vmcount_input    = raw_input("Which VM copy is this? (i.e., you need to test 3 of each machine for 24 hours. Is this machine 1, 2, or 3?) ")
local_input      = "0"
block_input      = "0"

#Generate a random number to add to the unique ID for this provider and VM combination in the test cycle
random_uid    = randint(0,1000000)
generated_uid = provider_input + vm_input + startdate_input + str(random_uid)

if disk_rand =='y':
    fio_rw = "Yes"

if disk_seq =='y':
    fio_seq = "Yes"

if internal_net_tests == 'y':
    internal_net_ip = raw_input('Please enter the IP address of the server you are trying to connect to: ')
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
        sub.call(['./geekbench_x86_64','--no-upload','--export-json', 'gb.json'])

        #OPEN the file
        geekbench_json = open('gb.json')

        #Load the JSON file
        data = json.load(geekbench_json)
        if iterator == 1:
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

    if pts_tests == 'y':
        #Run Phoronix Test Suite
        for test in pts_available_tests:
            x = 'TEST_RESULTS_NAME=' + test + ' phoronix-test-suite batch-benchmark ' + test
            print x
            os.system(x)

        #Open the result output
        pts_results_iteration = 'test-' + str(iterator) + '.xml'
        for test in pts_available_tests:
            xml = open(str(os.getenv('HOME')) + '/.phoronix-test-suite/test-results/' + test +'/' + pts_results_iteration).read()
            xml = bs(xml, 'xml')
            pts_available_tests[test] = float(str(xml.PhoronixTestSuite.Result.Data.Value.string))


    #Run Disk Tests if disk tests are enabled   
    #List of disk parameters
    disk_options = [fio_seq_rw,fio_rand_rw]

    def fio_command_generator(option):
        global fio_command
        fio_command = ['fio',option,fio_filename,fio_blocksize,fio_filesize,fio_numjobs,fio_runtime,fio_direct,'-time_based','--output-format=json','--output=fio.json','-time_based' ,'-group_reporting','-exitall']
        return fio_command

    def fio_async_command_generator(option):
        global fio_command
        fio_command = ['fio',option,fio_filename,"-bs=128k","-size=128M",-numjobs=8,fio_runtime,fio_direct,'-iodepth=32','-ioengine=libaio','-time_based','--output-format=json','--output=fio.json','-time_based' ,'-group_reporting','-exitall']
        return fio_command

    def spider_egg_exterminator():
        fio_json.close()
        os.remove(fio_json_file)
        #Remove the spider eggs I laid.
        for baby_spiders in range(0,spider_hatchlings):
            spideregg_file = "spider_eggs." + str(baby_spiders) + ".0"
            try:
		    os.remove(spideregg_file)
            except:
                print 'no file'

    if disk_rand == 'y':
        sub.call(fio_command_generator(disk_options[0]))
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

        spider_egg_exterminator()

        if fio_async =='y':
            sub.call(fio_async_command_generator(disk_options[0]))
            #OPEN the file
            fio_json = open(fio_json_file)
            #Load the JSON file
            fio_data = json.load(fio_json)

            runtime_read_rand_async  = str(fio_data['jobs'][0]        ['read']           ['runtime'])
            runtime_write_rand_async = str(fio_data['jobs'][0]        ['write']          ['runtime'])
            ops_read_rand_async      = str(fio_data['disk_util'][0]   ['read_ios'])
            ops_write_rand_async     = str(fio_data['disk_util'][0]   ['write_ios'])
            io_read_rand_async       = str(fio_data['jobs'][0]        ['read']           ['io_bytes'])
            io_write_rand_async      = str(fio_data['jobs'][0]        ['write']          ['io_bytes'])
            iops_read_rand_async     = str(fio_data['jobs'][0]        ['read']           ['iops'])
            iops_write_rand_async    = str(fio_data['jobs'][0]        ['write']          ['iops'])
            bw_read_rand_async       = str(fio_data['jobs'][0]        ['read']           ['bw'])
            bw_write_rand_async      = str(fio_data['jobs'][0]        ['write']          ['bw'])
            ticks_read_rand_async    = str(fio_data['disk_util'][0]   ['read_ticks'])
            ticks_write_rand_async   = str(fio_data['disk_util'][0]   ['write_ticks'])

            spider_egg_exterminator()


    if disk_seq == 'y':
        sub.call(fio_command_generator(disk_options[1]))
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

        spider_egg_exterminator()
        if fio_async =='y':
            sub.call(fio_async_command_generator(disk_options[1]))
            #OPEN the file
            fio_json = open(fio_json_file)
            #Load the JSON file
            fio_data = json.load(fio_json)

            runtime_read_seq_async  = str(fio_data['jobs'][0]        ['read']           ['runtime'])
            runtime_write_seq_async = str(fio_data['jobs'][0]        ['write']          ['runtime'])
            ops_read_seq_async      = str(fio_data['disk_util'][0]   ['read_ios'])
            ops_write_seq_async     = str(fio_data['disk_util'][0]   ['write_ios'])
            io_read_seq_async       = str(fio_data['jobs'][0]        ['read']           ['io_bytes'])
            io_write_seq_async      = str(fio_data['jobs'][0]        ['write']          ['io_bytes'])
            iops_read_seq_async     = str(fio_data['jobs'][0]        ['read']           ['iops'])
            iops_write_seq_async    = str(fio_data['jobs'][0]        ['write']          ['iops'])
            bw_read_seq_async       = str(fio_data['jobs'][0]        ['read']           ['bw'])
            bw_write_seq_async      = str(fio_data['jobs'][0]        ['write']          ['bw'])
            ticks_read_seq_async    = str(fio_data['disk_util'][0]   ['read_ticks'])
            ticks_write_seq_async   = str(fio_data['disk_util'][0]   ['write_ticks'])

            spider_egg_exterminator()

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

    if disk_rand =='n' and disk_seq =='n':
        fio_rw = "n/a"
        fio_seq = "n/a"
        fio_blocksize = 0
        fio_filesize = 0
        fio_numjobs = 0
        fio_direct_val = 0

#====================GLOBAL TRANSMITTING====================#
    #Transmit data back to Olympuss
    print "Transmitting to Olympus"
    if iterator == 1:
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
            block          = block_input,
            disk_rand      = fio_rw,
            disk_seq       = fio_seq,
            disk_blocksize = fio_blocksize,
            disk_filesize  = fio_filesize,
            disk_numjobs   = fio_numjobs,
            disk_direct    = fio_direct_val)
        print "Transfer 1"
        session.add(Open_Olympus)
        print "Transfer 2"
        session.commit()
        print "Transfer Complete"

    #Parse data into System Results if processor & memory tests were requested
    if system_tests == 'y':
        Hermes_System_Results   = Hermes_System(
            uid                 = generated_uid,
            iteration           = iterator,
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
        os.remove('gb.json')
        #Close the Geekbench file when you're done with it
        geekbench_json.close()

    if pts_tests == 'y':
        Hermes_pts              = HermesPTS(
            uid                 = generated_uid,
            iteration           = iterator,
            compress7zip        = pts_available_tests['compress-7zip'],
            phpbench            = pts_available_tests['phpbench'],
            mp3encode           = pts_available_tests['encode-mp3'],
            x264                = pts_available_tests['x264'])
        session.add(Hermes_pts)
        session.commit()

    #parse data into Disk Results if disk tests were requested
    if disk_rand == 'y':
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
        session.commit()
        if fio_async == 'y':
            Hermes_Rand_Async   = HermesRandasync(
                uid                 = generated_uid,
                iteration           = iterator,
                read_runtime        = runtime_read_rand_async,
                write_runtime       = runtime_write_rand_async,
                read_iops           = iops_read_rand_async,
                read_io             = io_read_rand_async,
                read_bw             = bw_read_rand_async,
                read_ticks          = ticks_read_rand_async,
                write_iops          = iops_write_rand_async,
                write_io            = io_write_rand_async,
                write_bw            = bw_write_rand_async,
                write_ticks         = ticks_write_rand_async)
            session.add(Hermes_Rand_Async)
            session.commit()

    if disk_seq == 'y':
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
        session.commit()
        if fio_async == 'y':
            Hermes_Seq_Async    = HermesSeqasync(
                uid                 = generated_uid,
                iteration           = iterator,
                read_runtime        = runtime_read_seq_async,
                write_runtime       = runtime_write_seq_async,
                read_iops           = iops_read_seq_async,
                read_io             = io_read_seq_async,
                read_bw             = bw_read_seq_async,
                read_ticks          = ticks_read_seq_async,
                write_iops          = iops_write_seq_async,
                write_io            = io_write_seq_async,
                write_bw            = bw_write_seq_async,
                write_ticks         = ticks_write_seq_async)
            session.add(Hermes_Seq_Async)
            session.commit()

    if internal_net_tests == 'y':
        Hermes_Net              = HermesNet(
            uid                 = generated_uid,
            iteration           = iterator,
            transfer_mb         = internal_network_data,
            bandwidth_mb        = internal_network_bandwidth)
        session.add(Hermes_Net)
        session.commit()

    iterator = iterator + 1
    #Any delay before the next round is executed
    sleep(sleeptime)

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