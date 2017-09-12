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

            if fields[0] == "[OVERALL]":
                if fields[1] == "RunTime(ms)":
                    self.__dataTable['overall_run_time_ms'] = fields[2]
                if fields[1] == "Throughput(ops/sec)":
                    self.__dataTable['overall_thruput_ops'] = fields[2]
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

    def __init__(self, testFile, loadResFile, runResFile):
        __testWorkload = None
        __loadRes = None
        __runRes = None
        self.__testWorkload = YCSBTestSpecFile(testFile)
        self.__loadRes = YCSBOutputFile(loadResFile)
        self.__runRes = YCSBOutputFile(runResFile)
    # end  __init__(self, testFile, loadResFile, runResFile):

    # begin
    def printSummary(self):
        testWLData = self.__testWorkload.getDataTable()
        loadData = self.__loadRes.getDataTable()
        runData = self.__runRes.getDataTable()
        
        print testWLData['recordcount'] + ',' + testWLData['operationcount'] + ',' + \
            testWLData['fieldcount'] + ',' + testWLData['fieldlength'] + ',' + \
            loadData['overall_run_time_ms'] + ',' \
            + loadData['overall_thruput_ops'] + ',' + \
            runData['overall_run_time_ms'] + ',' + \
            runData['overall_thruput_ops']
            
    # end
        
# end YCSBIndTest


# main block
if __name__ == "__main__":
    testHandler = YCSBIndTest(sys.argv[1], sys.argv[2], sys.argv[3])
    testHandler.printSummary()
