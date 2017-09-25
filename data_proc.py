#
# Sample graphing / CSV data manipulation script.
#

import os
import sys
import numpy as np
from data_table_ops import DataTable
from data_graph import DataGraph

# --- begin main body ---- #
if __name__ != "__main__": exit(0)

inputCSVFile = sys.argv[1]
outputCSVFile = sys.argv[2]
outputBarCh1 = sys.argv[3]
outputMultiCh1 = sys.argv[4]

dt1 = DataTable()
dt1.importDataFromCSV(inputCSVFile)

dt1.insertColumn( dt1.getColumnCount() + 1, "iops_seq_ops",\
                  dt1.getColumnSumByName("iops_read_seq", "iops_write_seq") )

dt1.exportDataToCSV( outputCSVFile )

esxi25sel = dt1.getRowsByIndex( dt1.getIndexSingleSelection("provider", ["esxi25pct-"]) )
memmulti25 = esxi25sel.getFloatAvg( esxi25sel.getColumnByName("memmulti") )

esxi50sel = dt1.getRowsByIndex( dt1.getIndexSingleSelection("provider", ["esxi50pct-"]) )
memmulti50 = esxi50sel.getFloatAvg( esxi50sel.getColumnByName("memmulti") )

esxi75sel = dt1.getRowsByIndex( dt1.getIndexSingleSelection("provider", ["esxi75pct-"]) )
memmulti75 = esxi25sel.getFloatAvg( esxi75sel.getColumnByName("memmulti") )

esxi100sel = dt1.getRowsByIndex( dt1.getIndexSingleSelection("provider", ["esxi100pct-"]) )
memmulti100 = esxi100sel.getFloatAvg( esxi25sel.getColumnByName("memmulti") )

dg1 = DataGraph()

dg1.drawBarGraph( {'values_matrix':\
                   [['Groupings', '25%', '50%', '75%', '100%'],\
                    ['ESXi', memmulti25, memmulti50, memmulti75, memmulti100]],
                   'color_list' : ['b'],
                   'title' : 'Mem multi',
                   'xlabel' : 'VM Engagement Percentage',
                   'ylabel' : 'Memmulti',
                   'output_file_path' : outputBarCh1,
                   'bar_width' : 0.05,
                   'opacity' : 0.8} )

mmultiMin = np.min( [memmulti25, memmulti50, memmulti75, memmulti100] )
mmultiMax = np.max( [memmulti25, memmulti50, memmulti75, memmulti100] )
range = mmultiMax - mmultiMin

dg1.drawMulti2DGraph( { 'values_matrix' :\
                        [[ [25.0, 50.0, 75.0, 100.0], \
                           [memmulti25, memmulti50, memmulti75, memmulti100], 'bo' ]],
                        'graph_text' : \
                        [1, mmultiMax + 10, "Blue = mmulti"],
                        'title' : 'Mmulti',
                        'xlabel' : 'Engagement percentage',
                        'ylabel' : 'Mmulti',
                        'xrange' : [0, 120],
                        'yrange' : [mmultiMin - 0.2 * range, \
                                    mmultiMax + 0.2 * range],
                        'output_file_path' : outputMultiCh1} )
