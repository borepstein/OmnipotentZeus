<P>You must install these prerequisites in your windows machine before running the script. Please follow the steps below:
<P><B>1. Install Python 2.7 and set path</B>
<P>https://www.python.org/ftp/python/2.7.10/python-2.7.10.amd64.msi
<P><B>2. Install pip and set path</B>
<P>To install pip, securely download get-pip.py from https://bootstrap.pypa.io/get-pip.py
Then run the following (which may require administrator access):
<P>```python get-pip.py```
<P><B>3. Install .NET framework 4.0</B>
<P>http://download.microsoft.com/download/1/B/E/1BE39E79-7E39-46A3-96FF-047F95396215/dotNetFx40_Full_setup.exe
<P><B>4. Install MySQL Database server</B>
<P>http://dev.mysql.com/get/Downloads/MySQLInstaller/mysql-installer-web-community-5.6.26.0.msi
<P><B>5. Install git</B>
<P>http://git-scm.com/download/win
<P><B>6. Install wget for Windows and set path</B>
<P>http://downloads.sourceforge.net/gnuwin32/wget-1.11.4-1-setup.exe
<P><B>7. Clone the repository</B>
<P>```git clone -b inapp-windows-script https://github.com/kennymuli/OmnipotentZeus.git```
<P><B>8. Run the program</B>
<P>```./OmnipotentZeus/run_win.bat```
<P><B>Note:</B> The default installation path for Geekbench and FIO is C:/Program Files (x86)/
<P>If you have installed Geekbench or FIO in a different path other than mentioned above, please remember to specify it in: /OmnipotentZeus/projects/test.py
