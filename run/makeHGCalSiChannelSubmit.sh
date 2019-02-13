#!/bin/bash

# Type of analysis: (motherboard/hgcroc)
runType=$1

#Delete all current files
cd /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/

rm -Rf ./jobs
mkdir jobs
cd jobs
mkdir log err out sub
for layer_idx in {1..36}; do mkdir log/lay$layer_idx; mkdir err/lay$layer_idx; mkdir out/lay$layer_idx; mkdir sub/lay$layer_idx; done
#rm log/lay*/log_HGCalSiChannel_lay*
#rm err/lay*/err_HGCalSiChannel_lay*
#rm out/lay*/out_HGCalSiChannel_lay*
#rm sub/lay*/submit_HGCalSiChannel_lay*

cd /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/jobs/sub 

for layer_idx in {1..36}
  do
    cd lay$layer_idx
    for file_idx in {1..10}
      do
        echo "executable          = /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/runAnalyzer.sh" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
        echo "arguments           = $runType $file_idx -1 $layer_idx" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
        echo "output              = /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/jobs/out/lay$layer_idx/out_HGCalSiChannel_lay"$layer_idx"_"$file_idx".out" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
        echo "error               = /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/jobs/err/lay$layer_idx/err_HGCalSiChannel_lay"$layer_idx"_"$file_idx".err" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
        echo "log                 = /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/jobs/log/lay$layer_idx/log_HGCalSiChannel_lay"$layer_idx"_"$file_idx".log" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
        echo "+JobFlavour         = \"workday\"" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
        echo "queue" >> submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
      done
    cd ..
  done
    
cd /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/
