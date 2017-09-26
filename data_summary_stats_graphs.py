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
