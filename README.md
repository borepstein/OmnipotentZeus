**Description:** This package is designed to be a testbed for measuring virtual machine performance in scalable cloud environments for Linux platforms. It uses a single table called ```olympus``` for storing test results. It uses the following tests:

```- Geekbench```

```- iperf```

```- FIO```

```- iozone```

```- Sysbench```

```- Apachebench```

```- SPEC```

**Instructions:**

**1. Open conf.py and make necessary configuration changes**

**Note:** Uncomment SPEC installation lines in ```run_ubuntu.sh``` or ```run_centos.sh```, if you wish to run teh SPEC CPU 2006 test.

**2. Run the script**

```cd omnipotentzeus```

For Debian based machines, run:

```sudo ./run_ubuntu.sh```

For RHEL based machines, run:

```sudo ./run_centos.sh```