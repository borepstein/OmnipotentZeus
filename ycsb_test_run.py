import os
import sys
import csv

# begin YCSBOutputFile()
class YCSBOutputFile(): 
    # begin __init__(self, outputFile)
    def __init__(self, outputFilePath):
        self.__dataTable = {}
        self.__dataTable['file_path'] = outputFilePath

        fhandle = open(outputFilePath, 'r')

        for line in fhandle:
            fields = line.split(',')

            for i in range(0, len(fields)):
                fields[i] = fields[i].lstrip().strip()

            if len(fields) != 3: continue            

            if fields[0] not in self.__dataTable.keys():
                self.__dataTable[ fields[0] ] = {}
                
            self.__dataTable[fields[0]][fields[1]] = fields[2]
            
        fhandle.close()
        
    # end __init__(self, outputFile)

    def getDataTable(self): return self.__dataTable

    
# end YCSBOutputFile()

# begin YCSBTestSpecFile()
class YCSBTestSpecFile():
    # begin __init__(self, specFilePath)
    def __init__(self, specFilePath):
        self.__dataTable = {}
        self.__dataTable['file_path'] = specFilePath

        fhandle = open(specFilePath, 'r')

        for line in fhandle:
            line = ((line.split('#'))[0]).lstrip().strip()
            fields = line.split('=')

            if len( fields ) == 2:
                self.__dataTable[ fields[0] ] = fields[1]
            
        fhandle.close()
    # end __init__(self, specFilePath)

    def getDataTable(self): return self.__dataTable
    
# end YCSBTestSpecFile()

# begin YCSBIndTest
class YCSBIndTest():
    # begin  __init__(self, testFile, loadResFile, runResFile):

    def __init__(self, testFile, loadResFile, runResFile, summaryOutputFile = None,
                 provider = None, clusterSize=None, threadCount=None, dbDeviceType=None,
                 dbReplFactor=None):
        self.__dataTable = {}
        self.__dataTable['ycsb_test_file_desc'] = YCSBTestSpecFile(testFile)
        self.__dataTable['ycsb_load_out_file_desc'] = YCSBOutputFile(loadResFile)
        self.__dataTable['ycsb_run_out_file_desc'] = YCSBOutputFile(runResFile)
        self.__dataTable['output_file_path'] = summaryOutputFile
        self.__dataTable['provider'] = provider
        self.__dataTable['cluster_size'] = clusterSize
        self.__dataTable['thread_count'] = threadCount
        self.__dataTable['db_device_type'] = dbDeviceType
        self.__dataTable['db_repl_factor'] = dbReplFactor
    # end  __init__(self, testFile, loadResFile, runResFile):

    # begin printSummary(self)
    def printSummary(self):
        testWLData = self.__dataTable['ycsb_test_file_desc'].getDataTable()
        loadData = self.__dataTable['ycsb_load_out_file_desc'].getDataTable()
        runData = self.__dataTable['ycsb_run_out_file_desc'].getDataTable()

        outputStr = self.__dataTable['provider'] + ',' 
        outputStr += self.__dataTable['cluster_size'] + ','
        outputStr += self.__dataTable['thread_count'] + ','
        outputStr += self.__dataTable['db_device_type'] + ','
        outputStr += self.__dataTable['db_repl_factor'] + ','
        outputStr += testWLData['recordcount'] + ',' + testWLData['operationcount'] + ','
        outputStr += testWLData['fieldcount'] + ',' + testWLData['fieldlength'] + ','
        outputStr += loadData['[OVERALL]']['RunTime(ms)'] + ',' 
        outputStr += loadData['[OVERALL]']['Throughput(ops/sec)'] + ','
        outputStr += loadData['[INSERT]']['AverageLatency(us)'] + ','
        outputStr += loadData['[INSERT]']['MinLatency(us)'] + ','
        outputStr += loadData['[INSERT]']['MaxLatency(us)'] + ','
        outputStr += loadData['[INSERT]']['95thPercentileLatency(us)'] + ','
        outputStr += loadData['[INSERT]']['99thPercentileLatency(us)'] + ','
        outputStr += runData['[OVERALL]']['RunTime(ms)'] + ',' 
        outputStr += runData['[OVERALL]']['Throughput(ops/sec)']

        if '[READ]' in runData.keys():
            outputStr += runData['[READ]']['AverageLatency(us)'] + ','
            outputStr += runData['[READ]']['MinLatency(us)'] + ','
            outputStr += runData['[READ]']['MaxLatency(us)'] + ','
            outputStr += runData['[READ]']['95thPercentileLatency(us)'] + ','
            outputStr += runData['[READ]']['99thPercentileLatency(us)'] + ','
        else:
            outputStr += "Null" + ','
            outputStr += "Null" + ','
            outputStr += "Null" + ','
            outputStr += "Null" + ','
            outputStr += "Null" + ','

        if '[UPDATE]' in runData.keys():
            outputStr += runData['[UPDATE]']['AverageLatency(us)'] + ','
            outputStr += runData['[UPDATE]']['MinLatency(us)'] + ','
            outputStr += runData['[UPDATE]']['MaxLatency(us)'] + ','
            outputStr += runData['[UPDATE]']['95thPercentileLatency(us)'] + ','
            outputStr += runData['[UPDATE]']['99thPercentileLatency(us)']
        else:
            outputStr += "Null" + ','
            outputStr += "Null" + ','
            outputStr += "Null" + ','
            outputStr += "Null" + ','
            outputStr += "Null" 

        if self.__dataTable['output_file_path'] is None:
            print outputStr
            return

        fh = open( self.__dataTable['output_file_path'], 'w')
        fh.write( outputStr )
        fh.close()
            
    # end printSummary(self)

    def getDataTable(self): return self.__dataTable()
        
# end YCSBIndTest


# main block
if __name__ == "__main__":
    testHandler = YCSBIndTest(sys.argv[1], sys.argv[2], sys.argv[3],
                              sys.argv[4], sys.argv[5], sys.argv[6],
                              sys.argv[7], sys.argv[8], sys.argv[9],)
    testHandler.printSummary()
