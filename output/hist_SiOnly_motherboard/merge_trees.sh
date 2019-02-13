#!/bin/bash

for layer_idx in {1..36}; do hadd -f HGCalOccupancy_SiOnly_layer$layer_idx.root lay$layer_idx/HGCalOccupancy_SiOnly_layer"$layer_idx"_*.root; done
