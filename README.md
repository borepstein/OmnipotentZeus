**Description:** This package is designed to be a testbed for measuring virtual machine performance in scalable cloud environments for Linux platforms. It uses a multi-table database structure for storing test results and is used to work in conjunction with ```SaltStack```. It uses the following tests:

```- Geekbench```

```- iperf```

```- FIO```

This package also includes the aggregate_gen.py script, which is used to generate aggregate data from the data tables of ```forecast``` DB.

**Instructions:**

**1. Open conf.py and make necessary configuration changes**

**2. Run the script**

```cd omnipotenthera```

For Debian based machines, run:

```sudo ./run_ubuntu.sh```

For RHEL based machines, run:

```sudo ./run_centos.sh```