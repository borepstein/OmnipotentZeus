<P><B>Description: </B>This package is designed to be a testbed for measuring virtual machine performance in a scalable, cloud environment. It uses the following tests:</P>
```a. Geekbench```
```b. iperf```
```c. FIO```
```d. iozone```
```e. Sysbench```
```f. Apachebench```
```g. SPEC```

<P><B>1. Open ```conf.py``` and make necessary configuration changes</B></P>
<P><B>Note: </B>Uncomment SPEC installation lines in ```run_ubuntu.sh``` or ```run_centos.sh```, if you wish to run teh SPEC CPU 2006 test.

<P><B>2. Install dependencies and run the script</B></P>
```cd omnipotentzeus```
<P>For Debian based machines, run:</P>
```sudo ./run_ubuntu.sh```
<P>For RHEL based machines, run:</P>
```sudo ./run_centos.sh```