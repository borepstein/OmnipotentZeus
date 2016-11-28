**Description:** This package is designed to be a testbed for measuring virtual machine performance in a scalable, cloud environment. It uses the following tests:</P>

```1. Geekbench```

```2. iperf```

```3. FIO```

```4. iozone```

```5. Sysbench```

```6. Apachebench```

```7. SPEC```


**1. Open conf.py and make necessary configuration changes**

**Note:** Uncomment SPEC installation lines in ```run_ubuntu.sh``` or ```run_centos.sh```, if you wish to run teh SPEC CPU 2006 test.

**2. Install dependencies and run the script**

```cd omnipotentzeus```

For Debian based machines, run:

```sudo ./run_ubuntu.sh```

For RHEL based machines, run:

```sudo ./run_centos.sh```