#
# Sample graphing / CSV data manipulation script.
#

import os
import sys
import json
import numpy as np
from data_table_ops import DataTable
from data_graph import DataGraph

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
outputBarCh1 =  configData['output']['directory_path'] + "bgr_mmulti1.png"
outputMultiCh1 = configData['output']['directory_path'] + "line_mmulti1.png"

dt1 = DataTable()
dt1.importDataFromCSV( inputCSVFile )

idFields = ["provider", "vcpu", "ram"]
dataFields = dt1.getColumnList()[15:]

providerList = sorted( set(dt1.getColumnByName("provider")) )
vcpuList = sorted( set(dt1.getColumnByName("vcpu")) )
ramList = sorted( set(dt1.getColumnByName("ram")) )

#-------- Begin: Cycling through data; generating CSV files ------------
for df in dataFields:
    outFpath = configData['output']['directory_path'] + df +".stats.csv"
    outColList = ["provider", "vcpu", "ram", "min", "5th percentile", \
                  "average", "stdev", "95th percentile", "max" ]
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
                          np.average( dfValList ),
                          np.std( dfValList ),
                          np.percentile( dfValList, 95 ),
                          np.max( dfValList ) ]
                    )
                except:
                    pass

    DataTable(outDataMatrix, outColList).exportDataToCSV(outFpath)

    cData = configData['conversion_data']
    metricGraphData = [['Groupings', '25%', '50%', '75%', '100%']]
    colorSetList = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    
    for vmt in ["small", "medium"]:
        metricGraphLbl = vmt + ":" + df
        metricGraphOutPath =  configData['output']['directory_path'] + \
                              metricGraphLbl + ".png"

        colorList = []
        matLineCount = 0

        # ---- begin: cycling through providers and variants
        for prov in cData['provider_list'].keys():
            
            graphLbl = cData['provider_list'][prov]['name'] + ":" \
                       + vmt + "--" + df
            valList = []
            
            for vari in ["25%", "50%", "75%", "100%"]:
                prv_full = cData['provider_list'][prov]['name'] + \
                           cData['provider_list'][prov]['variants'][vari]
                ind = dt1.getIndexSingleSelection("provider", prv_full)

                ind = dt1.getIndexSingleSelection("vcpu", \
                                                  str( [cData['provider_list']\
                                                   [prov]['vm_types']\
                                                   [vmt]['vcpu']] ),
                                                  ind)
                
                dt_temp = dt1.getRowsByIndex(ind)
                avg = dt_temp.getFloatAvg( dt_temp.getColumnByName(df) )
                
                if avg is None: avg = 0
                
                valList.append( avg )

            outFname = configData['output']['directory_path'] +\
                    graphLbl + ".png"

            if np.min( valList ) != 0 or np.max( valList ) != 0:
                metricGraphData.append( list([prov] + valList ) )
                colorList.append( \
                                  colorSetList[\
                                               matLineCount % \
                                               len(colorSetList)] )
                matLineCount += 1
                
                DataGraph().drawBarGraph( {
                    'values_matrix' : \
                    [ ['Groupings', '25%', '50%', '75%', '100%'],
                      list([prv_full] + valList)],
                    'color_list' : 'b',
                    'title' : graphLbl,
                    'xlabel' : 'VM Engagement Percentage',
                    'ylabel' : df,
                    'output_file_path' : outFname,
                    'bar_width' : 0.05,
                    'opacity' : 0.8
                    } )
        # ---- begin: cycling through providers and variants

        DataGraph().drawBarGraph( {
            'values_matrix' : metricGraphData,
            'color_list' : colorList,
            'title' : metricGraphLbl,
            'xlabel' : 'VM Engagement Percentage',
            'ylabel' : df,
            'output_file_path' : metricGraphOutPath,
            'bar_width' : 0.05,
            'opacity' : 0.8
        } )
#-------- Begin: Cycling through data; generating CSV files ------------
