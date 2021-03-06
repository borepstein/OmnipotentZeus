#
# Sample graphing / CSV data manipulation script.
#

import os
import sys
import json
import numpy as np
from data_table_ops import DataTable
from data_graph import DataGraph

#------- begin: generateMetricSummary
def generateMetricSummary(df):
    outFpath = configData['output']['directory_path'] + df +".stats.csv"
    outColList = ["provider", "vcpu", "ram", "min", "5th percentile", \
                  "median", "average", "stdev", "95th percentile", "max" ]
    outDataMatrix = []
    
    for prov in providerList:
        for vcpu in vcpuList:
            for ram in ramList:
                ind = dt1.getIndexSingleSelection("provider", [prov])
                ind = dt1.getIndexSingleSelection("vcpu", [vcpu], ind)
                ind = dt1.getIndexSingleSelection("ram", [ram], ind)

                if ind == []:
                    continue
            
                selDT = dt1.getRowsByIndex(ind)

                dfValList = selDT.getFloatsOnly(
                    selDT.getColumnByName( df )
                )

                try:
                    outDataMatrix.append(
                        [ prov,
                          vcpu,
                          ram,
                          np.min( dfValList ),
                          np.percentile( dfValList, 5 ),
                          np.median( dfValList ),
                          np.average( dfValList ),
                          np.std( dfValList ),
                          np.percentile( dfValList, 95 ),
                          np.max( dfValList ) ]
                    )
                except:
                    pass

    # Bail out if there is no data.
    if len(outDataMatrix) <= 1: return
    
    DataTable(outDataMatrix, outColList).exportDataToCSV(outFpath)
#------- end: generateMetricSummary

#------- begin: processGraphs
def processGraphs(df):
    cData = configData['conversion_data']

    colorSetList = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    colorList = []

    vmtList = sorted( set(cData['provider_list'][cData['provider_list'].keys()[0]]['vm_types'].keys() ) )

    provList = sorted( set( cData['provider_list'].keys() ) )

    mainCycleCnt = 0
    valueMatrix = []
    allZeroFlag = True
    
    for prov in provList:
        mainCycleCnt += 1
        colorList.append(\
                         colorSetList[ (mainCycleCnt-1) % len(colorSetList)
                         ]  )

        valRow = [prov]
        
        for vmt in vmtList:
            variList = sorted( set( cData['provider_list'][prov]['variants'].keys() ) )

            ind = []
            for vari in variList:
                prv_full = cData['provider_list'][prov]['name'] + \
                           cData['provider_list'][prov]['variants'][vari]
                ind = sorted(
                    set( ind +
                         dt1.getIndexSingleSelection("provider", prv_full) ) )

            ind = dt1.getIndexSingleSelection("vcpu", \
                                              str( [cData['provider_list']\
                                                    [prov]['vm_types']\
                                                    [vmt]['vcpu']] ),\
                                              ind)
            
            dt_temp = dt1.getRowsByIndex(ind)
            floatList = dt_temp.getFloatsOnly( dt_temp.getColumnByName(df) )
            iterNumList = range(0, len(floatList))
            avg = 0
            
            if len( floatList ) > 0:
                avg = np.average( floatList )
                if allZeroFlag:
                    if np.min( floatList ) != 0 or \
                       np.max( floatList ) != 0:
                        allZeroFlag = False
                
            valRow.append( avg )

            # drawing the graph over iterations
            graphLbl = df + ":" + prov + ":" + vmt
            xLabel = "Iteration"
            yLabel= df
            outFname = configData['output']['directory_path'] + df + "." + prov + \
                       "." + vmt + \
                       ".iter.png"

            try:
                DataGraph().drawMulti2DGraph( {
                    'values_matrix' : [[iterNumList, floatList, 'bo']],
                    'graph_text' : [0, 0, ""],
                    'title' : graphLbl,
                    'xlabel' : xLabel,
                    'ylabel': yLabel,
                    'xrange' : [0, len(floatList) ],
                    'yrange' : [0, 1.25 * np.max(floatList) ],
                    'output_file_path' : outFname
                } )
            except:
                print "Error drawing iterations: " + graphLbl

        valueMatrix.append(valRow)

    # Exiting if no non zero values
    if allZeroFlag: return
    
    graphLbl = df + ":Provider:VM Size"
    outFname = configData['output']['directory_path'] + \
               df + ".prov.by-vm.png"
    
       
    dTable = { \
               'values_matrix' : \
               [['Groupings'] + vmtList] +
                 valueMatrix,
               'color_list' : colorList,
               'title' : graphLbl,
               'xlabel' : 'Provider',
               'ylabel' : df,
               'output_file_path' : outFname,
               'bar_width' : 0.05,
               'opacity' : 0.8
    }
    
    DataGraph().drawBarGraph( dTable )
#------- end: processGraphs

# --- begin main body ---- #
if __name__ != "__main__": exit(0)

try:
    f_h = open( sys.argv[1], "r")
except:
    exit(0)

configData = json.load( f_h )
f_h.close()

inputCSVFile = configData['input']['file_path']
outputCSVFile = configData['output']['file_path']

dt1 = DataTable()
dt1.importDataFromCSV( inputCSVFile )

idFields = ["provider", "vcpu", "ram"]
dataFields = dt1.getColumnList()[15:]

providerList = sorted( set(dt1.getColumnByName("provider")) )
vcpuList = sorted( set(dt1.getColumnByName("vcpu")) )
ramList = sorted( set(dt1.getColumnByName("ram")) )

#-------- Begin: Cycling through data; generating CSV files ------------
for df in dataFields:

    generateMetricSummary(df)
    
    processGraphs(df)
#-------- Begin: Cycling through data; generating CSV files ------------
