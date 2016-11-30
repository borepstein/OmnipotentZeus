**Description:** This package is designed to be a testbed for measuring virtual machine performance in scalable cloud environments for Windows platforms. It uses the following tests:

```- Geekbench```

```- iperf```

```- FIO```

```- iozone```

```- Sysbench```

```- Passmark```

```- SPEC```

**Instructions:**

You must install these prerequisites in your windows machine before running the script. Please follow the steps below:

**1. Install Python 2.7 and set path**

https://www.python.org/ftp/python/2.7.10/python-2.7.10.amd64.msi

**2. Install pip and set path**

To install pip, download get-pip.py from https://bootstrap.pypa.io/get-pip.py and then run the following (which may require administrator access):

```python get-pip.py```

**3. Install .NET framework 4.0**

http://download.microsoft.com/download/1/B/E/1BE39E79-7E39-46A3-96FF-047F95396215/dotNetFx40_Full_setup.exe

**4. Install MySQL Database server**

http://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-web-community-5.6.26.0.msi

**5. Install wget for Windows and set path**

http://downloads.sourceforge.net/gnuwin32/wget-1.11.4-1-setup.exe

**6. Open conf.py and make necessary configuration changes**

**7. Install dependencies and run the script**

```cd omnipotentzeus-windows```

```run_win.bat```

**Note:** The default installation path for Geekbench is ```C:\Program Files (x86)``` and for FIO is ```C:\Program Files```

If you have installed Geekbench or FIO in a different path other than those mentioned above, please remember to specify it in ```conf.py```