import os
import sys
import csv

# begin class DataTable()
class DataTable():

    # begin __init__
    def __init__(self, dataTable=None, columnList=None):
        self.__contentMatrix = {}
        self.__contentMatrix['column_list'] = []
        self.__contentMatrix['column_count'] = 0
        self.__contentMatrix['row_count'] = 0
        self.__contentMatrix['table'] = []
        
        if dataTable is None and columnList is None:
            return

        if columnList is None:
            if dataTable is None: return

            columnList = dataTable[0]
            del dataTable[0]

        self.fillInContent(dataTable, columnList)
    # end __init__

    # begin fillInContent 
    def fillInContent(self, dataTable, columnList):
        self.__contentMatrix['column_list'] = columnList
        self.__contentMatrix['column_count'] = len( self.__contentMatrix['column_list'] )

        for row in dataTable:
            ins_count = min( len(row), self.__contentMatrix['column_count'] )
            ins_row = []
            
            for j in range(0, ins_count):
                ins_row.append( row[j] )

            for j in range(ins_count, self.__contentMatrix['column_count']):
                ins_row.append( None )

            self.__contentMatrix['table'].append( ins_row )
            self.__contentMatrix['row_count'] += 1
    # begin fillInContent

    # begin importDataFromCSV
    def importDataFromCSV(self, csvFilePath):
        f_handle = open(self.__dataTable['input_data_file'])
        f_csv = csv.reader( f_handle, delimiter=',' )
        content_table = []
        column_list = []
        
        first_line = True
        
        for row in f_csv:
            if first_line:
                first_line = False
                column_list = list( row )
            else:
                content_table.append( row )

        f_handle.close()

        self.fillInContent(content_table, column_list)
    # end importDataFromCSV   

    # begin getColumnPosition(self, colName)
    def getColumnPosition(self, colName):
        try:
            return self.__contentMatrix['column_list'].index( colName )
        except:
            return -1
    # end getColumnPosition(self, colName)

    # begin getColumnByNumber(self, colNum)
    def getColumnByNumber(self, colNum):
        ret_list = []

        if colNum < 0 or colNum > self.__contentMatrix['column_count']:
            return ret_list

        for row in self.__contentMatrix['table']:
            ret_list.append( row[colNum] )

        return ret_list
    # end getColumnByNumber(self, colNum)

    def getColumnByName(self, colName):
        return self.getColumnByNumber( self.getColumnPosition(colName) )

    # begin getRowByNumber(self, rowNum)
    def getRowByNumber(self, rowNum):
        if rowNum < 0 or rowNum > self.__contentMatrix['row_count']:
            return []

        return self.__contentMatrix[ rowNum ]
    # begin getRowByNumber(self, rowNum)

    def getColumnList(self): return self.__contentMatrix['column_list']

    def getDataTableContent(self): return self.__contentMatrix['table']

    # begin insertColumn(self, colPos, colName, columnContent)
    def insertColumn(self, colPos, colName, columnContent):
        # Checking data for propriety.
        if colPos < 0 or colPos > self.__contentMatrix['column_count'] + 1 or \
           len(columnContent) != self.__contentMatrix['row_count'] or \
                                 colName == "": return

        try:
            self.__contentMatrix['column_list'].index( colName )
            return
        except:
            pass

        # Doing the actual insertion.
        self.__contentMatrix['column_count'] += 1
        self.__contentMatrix['column_list'].insert( colName ) 
            
        for i in range(0, self.__contentMatrix['row_count']):
            self.__contentMatrix['table'][i].insert( columnContent[i] )

    # end insertColumn(self, colPos, colName, columnContent)

    # begin insertRow(self, rowContent)
    def insertRow(self, rowContent):
        if len( rowContent  ) != self.__contentMatrix['column_count']: return

        self.__contentMatrix['row_count'] += 1
        self.__contentMatrix['table'].append( rowContent )
    # end insertRow(self, rowContent)

    # begin getIndexSingleSelection
    def getIndexSingleSelection(self, colName, valList, selIndex=None):
        retList = []
        if len( valList ) == 0: return retList
        
        colPos = self.getColumnPosition(colName)
        if colPos < 0: return retList

        if selIndex is None:
            runIndex = range(0, self.__contentMatrix['row_count'])
        else:
            runIndex = selIndex
            
        for i in runIndex:
            try:
                valList.index( self.__contentMatrix['table'][i][colPos] )
                retList.append(i)
            except:
                continue

        return retList
    # end getIndexSingleSelection
                                
# end class DataTable()
