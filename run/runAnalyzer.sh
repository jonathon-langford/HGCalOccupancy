#!/bin/bash

# Script to run the HGCal analysis: resource management in motherboards
cd /afs/cern.ch/work/j/jlangfor/HGCal/Occupancy_Studies/CMSSW_10_4_0_pre3/src/analysis/run
eval `scramv1 runtime -sh`

runType=$1
fileID=$2
maxEvents=$3
layer=$4

python $CMSSW_BASE/src/analysis/python/HGCal_occupancy_Analyzer_"$runType".py -i $fileID -n $maxEvents -l $layer
