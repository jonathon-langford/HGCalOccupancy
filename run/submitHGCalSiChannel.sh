#!/bin/bash

eval `scramv1 runtime -sh`

layer_idx=1
file_idx=1
for layer_idx in {1..36}
  do
    for file_idx in {1..10}
      do 
        condor_submit /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run/jobs/sub/lay$layer_idx/submit_HGCalSiChannel_lay"$layer_idx"_"$file_idx".sub
      done
  done


