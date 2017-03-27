#
# The script's main function is to process pre-formatted DB data (RDBMS)
# and outputing an Excel (.xlsx) file.
#

import os
import sys
import csv
import json
import argparse
import shutil
import socket
import xlsxwriter
import xml.etree.ElementTree as ET
import sqlalchemy

# local imports
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, create_engine, __version__
from sqlalchemy.ext.declarative import declarative_base

# constants
NUM_ARGS = 2
XML_DATABASE_TAG="database"
XML_DB_SERVER_TAG="db_server"
XML_HOST_ADDRESS_TAG="host"
XML_USER_TAG="user"
XML_PASSWORD_TAG="password"
XML_DB_TAG="db"
XML_PORT_TAG="port"
MYSQL_DEFAULT_PORT=3306

# end constants

# duplicate for prometheus.py declarations

Base = declarative_base()
metadata = MetaData()
tablename = 'olympus'

'''
class Olympus(Base):
    __tablename__ = tablename
    id = Column(Integer, primary_key=True)
    project = Column(String(30), nullable=False)
    uid = Column(String(50), nullable=False)
    provider = Column(String(30), nullable=False)
    region = Column(String(30), nullable=False)
    startdate = Column(String(30), nullable=False)
    iteration = Column(Integer, nullable=False)
    iteration_start_time = Column(String(50), nullable=False)
    processor = Column(String(100), nullable=True)
    vm = Column(String(30), nullable=False)
    vmcount = Column(Integer, nullable=False)
    vcpu = Column(Integer, nullable=False)
    ram = Column(Float(30), nullable=False)
    local = Column(Integer, nullable=False)
    block = Column(Integer, nullable=False)
    disk_rand = Column(String(10), nullable=True)
    disk_seq = Column(String(10), nullable=True)
    disk_blocksize = Column(String(20), nullable=True)
    disk_filesize = Column(String(20), nullable=True)
    disk_numjobs = Column(String(20), nullable=True)
    disk_direct = Column(String(20), nullable=True)
    runtime = Column(Float(30), nullable=True)
    intmulti = Column(Integer, nullable=True)
    floatmulti = Column(Integer, nullable=True)
    memmulti = Column(Integer, nullable=True)
    intsingle = Column(Integer, nullable=True)
    floatsingle = Column(Integer, nullable=True)
    memsingle = Column(Integer, nullable=True)
    totalmulti = Column(Integer, nullable=True)
    totalsingle = Column(Integer, nullable=True)
    aes = Column(Float(30), nullable=True)
    twofish = Column(Float(30), nullable=True)
    sha1 = Column(Float(30), nullable=True)
    sha2 = Column(Float(30), nullable=True)
    bzipcompression = Column(Float(30), nullable=True)
    bzipdecompression = Column(Float(30), nullable=True)
    jpegcompression = Column(Float(30), nullable=True)
    jpegdecompression = Column(Float(30), nullable=True)
    pngcompression = Column(Float(30), nullable=True)
    pngdecompression = Column(Float(30), nullable=True)
    sobel = Column(Float(30), nullable=True)
    lua = Column(Float(30), nullable=True)
    dijkstra = Column(Float(30), nullable=True)
    blackscholes = Column(String(50), nullable=True)
    mandelbrot = Column(Float(30), nullable=True)
    sharpenimage = Column(Float(30), nullable=True)
    blurimage = Column(Float(30), nullable=True)
    sgemm = Column(Float(30), nullable=True)
    dgemm = Column(Float(30), nullable=True)
    sfft = Column(Float(30), nullable=True)
    dfft = Column(Float(30), nullable=True)
    nbody = Column(Float(30), nullable=True)
    raytrace = Column(Float(30), nullable=True)
    copy = Column(Float(30), nullable=True)
    scale = Column(Float(30), nullable=True)
    add = Column(Float(30), nullable=True)
    triad = Column(Float(30), nullable=True)
    runtime_read_seq = Column(Float(30), nullable=True)
    runtime_write_seq = Column(Float(30), nullable=True)
    io_read_seq = Column(Float(30), nullable=True)
    io_write_seq = Column(Float(30), nullable=True)
    iops_read_seq = Column(Float(30), nullable=True)
    iops_write_seq = Column(Float(30), nullable=True)
    bw_read_seq = Column(Float(30), nullable=True)
    bw_write_seq = Column(Float(30), nullable=True)
    iops_read_100_seq = Column(Float(30), nullable=True)
    iops_write_100_seq = Column(Float(30), nullable=True)
    throughput_read_100_seq = Column(Float(30), nullable=True)
    throughput_write_100_seq = Column(Float(30), nullable=True)
    lat_read_100_seq = Column(Float(30), nullable=True)
    lat_write_100_seq = Column(Float(30), nullable=True)
    runtime_read_seq_async = Column(Float(30), nullable=True)
    runtime_write_seq_async = Column(Float(30), nullable=True)
    io_read_seq_async = Column(Float(30), nullable=True)
    io_write_seq_async = Column(Float(30), nullable=True)
    iops_read_seq_async = Column(Float(30), nullable=True)
    iops_write_seq_async = Column(Float(30), nullable=True)
    bw_read_seq_async = Column(Float(30), nullable=True)
    bw_write_seq_async = Column(Float(30), nullable=True)
    iops_read_100_seq_async = Column(Float(30), nullable=True)
    iops_write_100_seq_async = Column(Float(30), nullable=True)
    throughput_read_100_seq_async = Column(Float(30), nullable=True)
    throughput_write_100_seq_async = Column(Float(30), nullable=True)
    lat_read_100_seq_async = Column(Float(30), nullable=True)
    lat_write_100_seq_async = Column(Float(30), nullable=True)
    runtime_read_rand = Column(Float(30), nullable=True)
    runtime_write_rand = Column(Float(30), nullable=True)
    io_read_rand = Column(Float(30), nullable=True)
    io_write_rand = Column(Float(30), nullable=True)
    iops_read_rand = Column(Float(30), nullable=True)
    iops_write_rand = Column(Float(30), nullable=True)
    bw_read_rand = Column(Float(30), nullable=True)
    bw_write_rand = Column(Float(30), nullable=True)
    iops_read_100_rand = Column(Float(30), nullable=True)
    iops_write_100_rand = Column(Float(30), nullable=True)
    throughput_read_100_rand = Column(Float(30), nullable=True)
    throughput_write_100_rand = Column(Float(30), nullable=True)
    lat_read_100_rand = Column(Float(30), nullable=True)
    lat_write_100_rand = Column(Float(30), nullable=True)
    runtime_read_rand_async = Column(Float(30), nullable=True)
    runtime_write_rand_async = Column(Float(30), nullable=True)
    io_read_rand_async = Column(Float(30), nullable=True)
    io_write_rand_async = Column(Float(30), nullable=True)
    iops_read_rand_async = Column(Float(30), nullable=True)
    iops_write_rand_async = Column(Float(30), nullable=True)
    bw_read_rand_async = Column(Float(30), nullable=True)
    bw_write_rand_async = Column(Float(30), nullable=True)
    iops_read_100_rand_async = Column(Float(30), nullable=True)
    iops_write_100_rand_async = Column(Float(30), nullable=True)
    throughput_read_100_rand_async = Column(Float(30), nullable=True)
    throughput_write_100_rand_async = Column(Float(30), nullable=True)
    lat_read_100_rand_async = Column(Float(30), nullable=True)
    lat_write_100_rand_async = Column(Float(30), nullable=True)
    internal_network_data = Column(Float(30), nullable=True)
    internal_network_bandwidth = Column(Float(30), nullable=True)
    hostname = Column(String(100), nullable=True)
    concurrency_level = Column(Integer, nullable=True)
    completed_requests = Column(Integer, nullable=True)
    time_taken = Column(Float(30), nullable=True)
    requests_per_sec = Column(Float(30), nullable=True)
    percent_50 = Column(Integer, nullable=True)
    percent_66 = Column(Integer, nullable=True)
    percent_75 = Column(Integer, nullable=True)
    percent_80 = Column(Integer, nullable=True)
    percent_90 = Column(Integer, nullable=True)
    percent_95 = Column(Integer, nullable=True)
    percent_98 = Column(Integer, nullable=True)
    percent_99 = Column(Integer, nullable=True)
    percent_100 = Column(Integer, nullable=True)
    iozone_seq_writers = Column(Float(30), nullable=True)
    iozone_seq_rewriters = Column(Float(30), nullable=True)
    iozone_seq_readers = Column(Float(30), nullable=True)
    iozone_seq_rereaders = Column(Float(30), nullable=True)
    iozone_random_readers = Column(Float(30), nullable=True)
    iozone_random_writers = Column(Float(30), nullable=True)
    sysbench_seq_write = Column(Float(30), nullable=True)
    sysbench_seq_read = Column(Float(30), nullable=True)
    sysbench_rand_write = Column(Float(30), nullable=True)
    sysbench_rand_read = Column(Float(30), nullable=True)
    perlbench_base_copies = Column(String(20), nullable=True)
    perlbench_base_runtime = Column(String(20), nullable=True)
    perlbench_base_rate = Column(String(20), nullable=True)
    perlbench_peak_copies = Column(String(20), nullable=True)
    perlbench_peak_runtime = Column(String(20), nullable=True)
    perlbench_peak_rate = Column(String(20), nullable=True)
    bzip2_base_copies = Column(String(20), nullable=True)
    bzip2_base_runtime = Column(String(20), nullable=True)
    bzip2_base_rate = Column(String(20), nullable=True)
    bzip2_peak_copies = Column(String(20), nullable=True)
    bzip2_peak_runtime = Column(String(20), nullable=True)
    bzip2_peak_rate = Column(String(20), nullable=True)
    gcc_base_copies = Column(String(20), nullable=True)
    gcc_base_runtime = Column(String(20), nullable=True)
    gcc_base_rate = Column(String(20), nullable=True)
    gcc_peak_copies = Column(String(20), nullable=True)
    gcc_peak_runtime = Column(String(20), nullable=True)
    gcc_peak_rate = Column(String(20), nullable=True)
    mcf_base_copies = Column(String(20), nullable=True)
    mcf_base_runtime = Column(String(20), nullable=True)
    mcf_base_rate = Column(String(20), nullable=True)
    mcf_peak_copies = Column(String(20), nullable=True)
    mcf_peak_runtime = Column(String(20), nullable=True)
    mcf_peak_rate = Column(String(20), nullable=True)
    xalancbmk_base_copies = Column(String(20), nullable=True)
    xalancbmk_base_runtime = Column(String(20), nullable=True)
    xalancbmk_base_rate = Column(String(20), nullable=True)
    xalancbmk_peak_copies = Column(String(20), nullable=True)
    xalancbmk_peak_runtime = Column(String(20), nullable=True)
    xalancbmk_peak_rate = Column(String(20), nullable=True)
    soplex_base_copies = Column(String(20), nullable=True)
    soplex_base_runtime = Column(String(20), nullable=True)
    soplex_base_rate = Column(String(20), nullable=True)
    soplex_peak_copies = Column(String(20), nullable=True)
    soplex_peak_runtime = Column(String(20), nullable=True)
    soplex_peak_rate = Column(String(20), nullable=True)
    sphinx3_base_copies = Column(String(20), nullable=True)
    sphinx3_base_runtime = Column(String(20), nullable=True)
    sphinx3_base_rate = Column(String(20), nullable=True)
    sphinx3_peak_copies = Column(String(20), nullable=True)
    sphinx3_peak_runtime = Column(String(20), nullable=True)
    sphinx3_peak_rate = Column(String(20), nullable=True)
'''

# end duplicate for prometheus.py declarations

# class ArgHandler
class ArgHandler():
    __numArgs = None
    __argArr = None
    __inputFilePath = None
    __outputFilePath = None

    # __init__
    def __init__(self):
        self.__numArgs = len (sys.argv ) - 1

        if ( self.__numArgs != NUM_ARGS ):
            raise SyntaxError
        
        self.__argArr = sys.argv[1:]
        self.__inputFilePath = self.__argArr[0]
        self.__outputFilePath = self.__argArr[1]
        
    # end __init__

    def getNumArgs(self): return __numArgs
    
    def getInputFilePath(self): return self.__inputFilePath

    def getOutputFilePath(self): return self.__outputFilePath
    
# end class ArgHandler

# class PerfDataHandler
class PerfDataHandler():
    __dbConnectParams = {}
    __dbEngine = None
    __dbSession = None
    __dbTable = None
    
    def __init__(self): pass

    # __init__(self, dcConnParams)
    def __init__(self, dbConnParams):
        self.__dbConnectParams = dbConnParams
        self.establishDBConnection()
        self.establishDBSession()
        self.establishDBTable()
    # __init__(self, dcConnParams)

    def setDBConnectParams(self, dbConnParams): self.__dbConnectParams = dbConnParams

    def getDBConnectParams(self): return self.__dbConnectParams
    
    # establishDBConnection(self)
    def establishDBConnection(self):
        self.__dbEngine = create_engine("mysql://%s:%s@%s:%s/%s" %
                                   (self.__dbConnectParams[XML_USER_TAG],
                                    self.__dbConnectParams[XML_PASSWORD_TAG],
                                    self.__dbConnectParams[XML_HOST_ADDRESS_TAG],
                                    self.__dbConnectParams[XML_PORT_TAG],
                                    self.__dbConnectParams[XML_DB_TAG]))


    # end establishDBConnection(self)

    # establishDBTable(self)
    def establishDBTable(self):
        if self.__dbEngine is None: return

        metadata.reflect(bind=self.__dbEngine)
        self.__dbTable = Table(tablename, metadata)
    # end establishDBTable(self)

    # establishDBSession(self)
    def establishDBSession(self):
        if self.__dbEngine is None: return
        
        self.__dbSession = Session(bind=self.__dbEngine )
    # end establishDBSession(self)
        
    def getDBConnection(self): return self.__dbEngine

    def getDBSession(self): return self.__dbSession

    def getDBTable(self): return self.__dbTable
    
# end class PerfDataHandler

# class InputFileHandler
class InputFileHandler():
    __filePath = None
    __xmlTree = None
    __xmlTreeRoot = None
    __dbConnectParams = {}
    
    # __init__ (fname)
    def __init__(self, fname):
        self.__filePath = fname

        if self.__filePath is None: return
        
        self.__xmlTree = ET.parse( self.__filePath )
        self.__xmlTreeRoot = self.__xmlTree.getroot()

        for member in self.__xmlTreeRoot:
            if member.tag == XML_DATABASE_TAG:
                for subm in member:
                    if subm.tag == XML_DB_SERVER_TAG:
                        for subm1 in subm:
                            self.__dbConnectParams[subm1.tag] = subm1.text
                        break
                break
            
    # end __init__ (fname)

    def getFilePath(self): return self.__filePath

    def getXMLTree(self): return self.__xmlTree

    def getXMLTreeRoot(self): return self.__xmlTreeRoot

    def getDBConnectParams(self): return self.__dbConnectParams

# end class InputHandler

# class OutputFileHandler
class OutputFileHandler():
    __filePath = None
    __workbook = None
    __rawDataTable = None
    __dbSession = None
    
    # WS formating constants
    __raw_tab_name = "Raw"
    

    # __init__(self, fname)
    def __init__(self, fname):
        self.__filePath = fname
        self.__workbook = xlsxwriter.Workbook( self.__filePath )
    # __init__(self, fname)

    def getFilePath(self): return self.__filePath

    def getWorkBook(self): return self.__workbook

    def setRawDataTable(self, dbTable): self.__rawDataTable = dbTable

    def getRawDataTable(self): return self.__rawDataTable

    def setDBSession(self, dbSession): self.__dbSession = dbSession

    def getDBSession(self): return self.__dbSession

    # fillRawTab(self)
    def fillRawTab(self):
        ws = self.__workbook.add_worksheet(self.__raw_tab_name)
        
        if (self.__rawDataTable is None) or \
           (self.__dbSession is None): return

        c_count = 0
        for col in self.__rawDataTable.columns:
            ws.write(0, c_count, str(col).split('.')[1] )
            c_count += 1

        r_count = 1
        for row_cont in self.__dbSession.query(self.__rawDataTable):
            c_count = 0
            for elem in row_cont:
                ws.write(r_count, c_count, elem)
                c_count += 1
            r_count += 1
    # end fillRawTab(self)
    
    # commitWorkBook(self):
    def commitWorkBook(self):
        self.__workbook.close()
    # end commitWorkBook(self):
        
# end class OutputFileHandler

#
# main function/block
#
def main():
    argH = ArgHandler()
    inputHandler = InputFileHandler( argH.getInputFilePath()  )
    perfDataConn = PerfDataHandler( inputHandler.getDBConnectParams() )
    table = perfDataConn.getDBTable()
    session = perfDataConn.getDBSession()
    outputHandler = OutputFileHandler( argH.getOutputFilePath() )
    outputHandler.setDBSession(session)
    outputHandler.setRawDataTable(table)
    outputHandler.fillRawTab()
    outputHandler.commitWorkBook()
# end main block

# main block invocation
if __name__ == "__main__": main()
# end main block invocation
