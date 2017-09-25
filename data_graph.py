import sys
import csv
import numpy as np

import matplotlib as mpl
from data_table_ops import DataTable

# Setting the proper backend.
mpl.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# begin  DataGraph()
class DataGraph():

    # begin __init__
    def __init__(self, inputDataTable=None, outputFilePath=None):
        self.__dataTable = {}
        self.__dataTable['input_data_table'] = inputDataTable
        self.__dataTable['output_file_path'] = outputFilePath
        self.__dataTable['input_data_file'] = None
    # end __init__

    def setInputDataTable(self, inputDataTable):
        self.__dataTable['input_data_table'] = inputDataTable

    def setOutputFilePath(self, outputFilePath):
        self.__dataTable['output_file_path'] = outputFilePath

    def getDataTable(self): return self.__dataTable

    # begin importDataFromCSV
    def importDataFromCSV(self, csvFilePath):
        self.__dataTable['input_data_file'] = csvFilePath

        f_handle = open(self.__dataTable['input_data_file'])
        f_csv = csv.reader( f_handle, delimiter=',' )
        content = []
        
        for row in f_csv:
            content.append( row )

        f_handle.close()

        self.__dataTable['input_data_table'] = content
    # end importDataFromCSV

    # begin getInputDataIndex
    def getInputDataIndex(self):
        index = None

        if self.__dataTable['input_data_table'] is not None:
            index = self.__dataTable['input_data_table'][0]
            
        return index
    # end getInputDataIndex

    # begin getFieldPosInIndex
    def getFieldPosInIndex(self, fieldName):
        pos = -1
        index = self.getInputDataIndex()

        if index is not None:
            for i in range(0, len(index)):
                if index[i] == fieldName:
                    pos = i
        
        return pos
    # end getFieldPosInIndex

    # begin getSingleFieldSelection
    def getSingleFieldSelection(self, fieldName, selCriteriaMatrix=None):
        selList = []

        fieldPos = self.getFieldPosInIndex(fieldName)

        if fieldPos < 0: return selList

        refCriteriaMatrix = selCriteriaMatrix

        if refCriteriaMatrix is None:
            selMatrixSize = 0
        else:
            selMatrixSize = len(refCriteriaMatrix)

        for i in range(0, selMatrixSize):
            refCriteriaMatrix[i][0] = \
                                      self.getFieldPosInIndex( refCriteriaMatrix[i][0] )
            if refCriteriaMatrix[i][0] < 0: return selList

        for i in range(1, len(self.__dataTable['input_data_table'])):
            inclFlag = True
            
            for j in range(0, selMatrixSize):
                if self.__dataTable['input_data_table'][i][refCriteriaMatrix[j][0]] \
                   != refCriteriaMatrix[j][1]:
                    inclFlag = False
                    break
                
            if inclFlag:
                selList.append(self.__dataTable['input_data_table'][i][fieldPos] )
                
        
        return selList
    # end getSingleFieldSelection

    # begin avgWithinSelection
    def avgWithinSelection(self, fieldName, selCriteriaMatrix):
        sel_list = self.getSingleFieldSelection(fieldName, selCriteriaMatrix)
        return( self.avg(sel_list) )
    # env avgWithinSelection
        
    # begin avg
    def avg(self, inList):
        avgVal = None
        count = 0

        for i in range(0, len(inList)):
            if inList[i] is None: continue

            try:
                floatVal = float( inList[i] )
            except:
                continue
            
            if avgVal is None: avgVal = 0
            count = count + 1
            avgVal = avgVal + floatVal

        if count > 0: avgVal = avgVal / count
        
        return avgVal
    # end avg

    # begin drawBarGraph
    def drawBarGraph(self, dataMatrix):
        #
        # Dictionary schema for dataMatrix
        # values_matrix: Matrix each row of which containes the name of the
        #          entity and the values series for all the graphs along
        #          with groupings:
        #
        #          Example[3 x 4]:
        #
        #          'Groupings'     Small       Medium        Large
        #          AWS              200         250           315
        #          DO               195         255           305
        #
        # color_list: ['b', 'g']
        #
        # title: 'CPU Performance'
        #
        # xlabel: 'Machine sizes'
        #
        # ylabel: 'Perf count'
        #
        # output_file_path: 'cpu_summ.png'
        #
        # bar_width: 0.35
        #
        # opacity: 0.8
        #

        # Get the number of groupings
        n_groups = len( dataMatrix['values_matrix'][0] ) - 1
        
        #create plot
        fig, ax = plt.subplots()
        index = np.arange(n_groups)
        
        for i in range(1, len(dataMatrix['values_matrix']) ):
            values_list = dataMatrix['values_matrix'][i][1:]

            try:
                plt.bar(index + dataMatrix['bar_width'] * (i - 1),
                        values_list, dataMatrix['bar_width'],
                        alpha = dataMatrix['opacity'],
                        color = dataMatrix['color_list'][i-1],
                        label = dataMatrix['values_matrix'][i][0])
            except:
                continue

        plt.xlabel( dataMatrix['xlabel'] )
        plt.ylabel( dataMatrix['ylabel'] )
        plt.title( dataMatrix['title'] )

        group_list = []

        for i in range(1, len(dataMatrix['values_matrix'][0]) ):
            group_list.append( dataMatrix['values_matrix'][0][i] )
        
        plt.xticks( index + dataMatrix['bar_width'], group_list )
        plt.legend()
        plt.tight_layout()
        plt.savefig( dataMatrix['output_file_path'] )
        plt.close()
    # end  drawBarGraph

    # begin drawMulti2DGraph(self, dataMatrix)
    def drawMulti2DGraph(self, dataMatrix):
        #
        # Dictionary schema for dataMatrix
        # values_matrix: Each row contins two equal length lists,
        # x-values and y-values and color/graph schema.
        # Example:
        # [ \
        # [[0, 2.5, 5, 7.5, 10], [3, 4, 7, 6, 5.5], 'bo'],
        # [[0, 2.5, 3, 4], [5.5, 2.5, 10, 12.5], 'ro']
        # ]
        #
        # graph_text: [x-coord, y-coord, text]
        # Example:
        # graph_text: [1, 10, "Blue = small VM\nRed = medium VM"]
        #
        # title: 'CPU Performance'
        #
        # xlabel: 'Machine sizes'
        #
        # ylabel: 'Perf count'
        #
        # xrange: [x-start, x-end]
        #
        # yrange: [y-start, y-end]
        #
        # output_file_path: 'cpu_summ.png'

        for row in dataMatrix['values_matrix']:
            plt.plot( row[0], row[1], row[2] )

        plt.axis( [float( dataMatrix['xrange'][0] ),\
                   float( dataMatrix['xrange'][1] ),
                   float( dataMatrix['yrange'][0] ),
                   float( dataMatrix['yrange'][1] ) ] )

        plt.xlabel( dataMatrix['xlabel'] )
        plt.ylabel( dataMatrix['ylabel'] )

        plt.text( dataMatrix['graph_text'][0],\
                  dataMatrix['graph_text'][1],\
                  dataMatrix['graph_text'][2] )
        
        plt.savefig( dataMatrix['output_file_path'] )
        plt.close()
    # end drawMulti2DGraph(self, dataMatrix)

# end  DataGraph

""" Sample usage scenario
# begin main block
if __name__ == "__main__":
    csvInput = sys.argv[1]
    graphOutput = sys.argv[2]

    # processing data through a DataGraph data
    dg = DataGraph()
    dg.importDataFromCSV( csvInput )

    provider_list = sorted( set(dg.getSingleFieldSelection("provider")) )
    cluster_list = sorted( set(dg.getSingleFieldSelection("cluster_size")) )
    db_device_type_list = sorted( set(dg.getSingleFieldSelection("db_device_type")) )

    draw_data_matrix = {}
    draw_data_matrix['title'] = 'Average load throughput'
    draw_data_matrix['xlabel'] = 'Provider'
    draw_data_matrix['ylabel'] = 'Load ops/sec'
    draw_data_matrix['output_file_path'] = graphOutput
    draw_data_matrix['bar_width'] = 0.35
    draw_data_matrix['opacity'] = 0.8
    draw_data_matrix['color_list'] = ['b', 'g', 'r']
    
    draw_data_matrix['values_matrix'] = []

    draw_data_matrix['values_matrix'].append( ['Groupings', 'RAM', 'SSD File', 'SSD Raw'] )
    
    draw_data_matrix['values_matrix'].append( ['AWS', \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','aws'],['db_device_type','ram']]), \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','aws'],['db_device_type','ssdfile']]), \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','aws'],['db_device_type','ssdraw']]) 
    ] )
 
    draw_data_matrix['values_matrix'].append( ['Internap', \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','inap'],['db_device_type','ram']]), \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','inap'],['db_device_type','ssdfile']]), \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','inap'],['db_device_type','ssdraw']])
    ] )

    draw_data_matrix['values_matrix'].append( ['Softlayer', \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','sl'],['db_device_type','ram']]), \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','sl'],['db_device_type','ssdfile']]), \
                                               dg.avgWithinSelection('Load-OVERALL-Throughput(ops/sec)', [['provider','sl'],['db_device_type','ssdraw']])
    ] )

    dg.drawBarGraph( draw_data_matrix )
        
# end main block

End sample usage scenario """
