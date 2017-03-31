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
from openpyxl import load_workbook
import xml.etree.ElementTree as ET
import sqlalchemy
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, create_engine, __version__
from sqlalchemy.ext.declarative import declarative_base

# constants
NUM_ARGS = 2
XML_SOURCE_TAG="source"
XML_XLSX_TAG="xlsx"
XML_FNAME_TAG="fname"
XML_PERF_DATA_SOURCE_TAG="perf_datasource"
XML_PRICING_DATA_SOURCE_TAG="pricing_datasource"
XML_XLSX_DATA_SOURCE_TAG="xlsx_report"
XML_DB_SERVER_TAG="db_server"
XML_HOST_ADDRESS_TAG="host"
XML_USER_TAG="user"
XML_PASSWORD_TAG="password"
XML_DB_TAG="db"
XML_PORT_TAG="port"
XML_TABLE_TAG="table"
XML_WORK_SHEET_TAG="worksheet"
XML_NAME_TAG="name"
MYSQL_DEFAULT_PORT=3306
XSLX_SERVERS_WS_NAME="Servers"
XSLX_PRICES_WS_NAME="Prices"
XSLX_RAW_WS_NAME="Raw"


# end constants

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
    __metadata = MetaData()
    __inputFileHandler = None
    
    def __init__(self): pass

    # __init__(self, inputFileHandler)
    def __init__(self, inputFileHandler):
        self.__inputFileHandler = inputFileHandler
        self.__dbConnectParams =  inputFileHandler.getDBConnectParams()
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

        if self.__metadata is None: return
    
        self.__metadata.reflect(bind=self.__dbEngine)
        self.__dbTable = Table(self.__dbConnectParams[XML_TABLE_TAG],\
                               self.__metadata)
        
    # end establishDBTable(self)

    # establishDBSession(self)
    def establishDBSession(self):
        if self.__dbEngine is None: return
        
        self.__dbSession = Session(bind=self.__dbEngine )
    # end establishDBSession(self)
        
    def getDBConnection(self): return self.__dbEngine

    def getDBSession(self): return self.__dbSession

    def getDBTable(self): return self.__dbTable

    def getInputFileHandler(self): return self.__inputFileHandler
# end class PerfDataHandler

# class PriceDataHandler
class PriceDataHandler():
    __outputFileHandler = None
    __priceXLSXFilePath = None
    __priceDataMatrix = None

    # __init__(self, outputFileHandler)
    def __init__(self, outputFileHandler):
        self.__outputFileHandler = outputFileHandler
        self.__priceXLSXFilePath = self.__getPriceXLSXFilePath()
        self.__priceDataMatrix = self.__getPriceDataMatrix()
    # end __init__(self, outputFileHandler)
        
    # __getPriceXLSXFilePath(self)
    def __getPriceXLSXFilePath(self):
        filePath = None
        xlsxConfirmed = False
        xmlTree = self.__outputFileHandler.getInputFileHandler().getXMLTree()

        for member in xmlTree.getroot():
            if member.tag == XML_PRICING_DATA_SOURCE_TAG:
                for subm in member:
                    if (subm.tag == XML_SOURCE_TAG) and \
                       (subm.text == XML_XLSX_TAG):
                        xlsxConfirmed = True

                    if (subm.tag == XML_FNAME_TAG):
                        filePath = subm.text
                break
            
        if xlsxConfirmed:
            return filePath

        return None
    # end __getPriceXLSXFilePath(self)

    def getPriceXLSXFilePath(self): return self.__priceXLSXFilePath

    # __getPriceDataMatrix(self)
    def __getPriceDataMatrix(self):
        priceDataMatrix = []

        priceWorkBook = load_workbook(filename=self.__priceXLSXFilePath,\
                                      read_only=True)

        priceWs = priceWorkBook[XSLX_PRICES_WS_NAME]

        for row in priceWs.rows:
            rowList=[]
            for cell in row:
                rowList.append( cell.value )
            priceDataMatrix.append( rowList )

        return priceDataMatrix
    # end __getPriceDataMatrix(self)

    def getPriceDataMatrix(self): return self.__priceDataMatrix
    
# end class PriceDataHandler

# class InputFileHandler
class InputFileHandler():
    __argHandler = None
    __filePath = None
    __xmlTree = None
    __xmlTreeRoot = None
    __dbConnectParams = {}
    __xlsx_report_tree = None
    __pricing_datasource_tree = None
    
    # __init__ (fname)
    def __init__(self, argHandler):
        self.__argHandler = argHandler
        self.__filePath = argHandler.getInputFilePath()

        if self.__filePath is None: return
        
        self.__xmlTree = ET.parse( self.__filePath )
        self.__xmlTreeRoot = self.__xmlTree.getroot()

        for member in self.__xmlTreeRoot:
            if member.tag == XML_PERF_DATA_SOURCE_TAG:
                for subm in member:
                    if subm.tag == XML_DB_SERVER_TAG:
                        for subm1 in subm:
                            self.__dbConnectParams[subm1.tag] = subm1.text

            if member.tag == XML_XLSX_DATA_SOURCE_TAG:
                self.__xlsx_report_tree = member

            if member.tag == XML_PRICING_DATA_SOURCE_TAG:
                self.__pricing_datasource_tree = member
                    
            
    # end __init__ (fname)

    def getArgHandler(self): return self.__argHandler

    def getFilePath(self): return self.__filePath

    def getXMLTree(self): return self.__xmlTree

    def getXMLTreeRoot(self): return self.__xmlTreeRoot

    def getDBConnectParams(self): return self.__dbConnectParams

    def getXLSXReportTree(self): return self.__xlsx_report_tree

    def getPricingDataSourceTree(self): return self.__pricing_datasource_tree
# end class InputHandler

# class OutputFileHandler
class OutputFileHandler():
    __argHandler = None
    __inputFileHandler = None
    __filePath = None
    __workbook = None
    __perfDataHandler = None
    __rawDataTable = None
    __dbSession = None
    __xlsx_report_tree = None
    
    # WS formating constants
    __raw_tab_name = "Raw"
    
    # __init__(self, argHandler, inputFileHandler)
    def __init__(self, argHandler, inputFileHandler):
        self.__argHandler = argHandler
        self.__inputFileHandler = inputFileHandler
        self.__filePath = argHandler.getOutputFilePath()
        self.__perfDataHandler = PerfDataHandler(inputFileHandler)
        self.__initWorkbook(self.__filePath)

        # Removing output file if it exists
        if os.path.isfile( self.__filePath ):
            os.remove( self.__filePath )
            
        xlsx_report_tree = inputFileHandler.getXLSXReportTree()
        dbTable = self.__perfDataHandler.getDBTable()
        dbSession = self.__perfDataHandler.getDBSession()

        if xlsx_report_tree is not None:
            self.setXLSXReportTree( xlsx_report_tree )

        if dbSession is not None:
            self.setDBSession( dbSession)
            
        if dbTable is not None:
            self.setRawDataTable( dbTable )

        self.__initWorksheets()
    # end __init__(self, fname, xlsx_report_tree, dbTable)

    # __initWorkbook(self, fname)
    def __initWorkbook(self, fname):
        self.__workbook = xlsxwriter.Workbook( fname )
    # end __initWorkbook(self, fname)

    # __initWorksheets(self)
    def __initWorksheets(self):        
        if self.__workbook is None: return

        if self.__xlsx_report_tree is None: return

        for member in self.__xlsx_report_tree:
            if member.tag == XML_WORK_SHEET_TAG:
                for subm in member:
                    if subm.tag == XML_NAME_TAG:
                        self.__workbook.add_worksheet(subm.text)
                        break
    # end __initWorksheets(self)

    def getArgHandler(self): return self.__argHandler

    def getInputFileHandler(self): return self.__inputFileHandler
    
    def setXLSXReportTree(self, xlsx_report_tree):
        self.__xlsx_report_tree = xlsx_report_tree

    def getFilePath(self): return self.__filePath

    def getWorkBook(self): return self.__workbook

    def setRawDataTable(self, dbTable): self.__rawDataTable = dbTable

    def getRawDataTable(self): return self.__rawDataTable

    def setDBSession(self, dbSession): self.__dbSession = dbSession

    def getDBSession(self): return self.__dbSession

    def getPerfDataHandler(self): return self.__perfDataHandler

    # fillRawTab(self)
    def fillRawTab(self):        
        if (self.__rawDataTable is None) or \
           (self.__dbSession is None): return
        
        ws = self.__workbook.get_worksheet_by_name(XSLX_RAW_WS_NAME)

        if ws is None: return

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

    # fillPricesTab(self)
    def fillPricesTab(self):
        ws = self.__workbook.get_worksheet_by_name(XSLX_PRICES_WS_NAME)

        if ws is None: return

        pdh = PriceDataHandler(self)

        pdm = pdh.getPriceDataMatrix()

        if pdm is None: return

        r_count = 0
        for row in pdm:
            c_count = 0
            for elem in row:
                ws.write(r_count, c_count, elem)
                c_count += 1
            r_count+=1
    # end  fillPricesTab(self)
    
    # commitWorkBook(self):
    def commitWorkBook(self):
        self.__workbook.close()
        self.__workbook = None
    # end commitWorkBook(self):
        
# end class OutputFileHandler

#
# main function/block
#
def main():
    argH = ArgHandler()
    inputH = InputFileHandler( argH )
    outputH = OutputFileHandler( argH, inputH )

    outputH.fillRawTab()
    outputH.fillPricesTab()
    outputH.commitWorkBook()
# end main block

# main block invocation
if __name__ == "__main__": main()
# end main block invocation
