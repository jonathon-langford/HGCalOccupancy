import ROOT
import pandas as pd
import sys
import os
from array import array
from optparse import OptionParser

shiftLayer = True #option to shift layer idx by -1 (value in ntuple = [1-36], value to output = [0,35])


##############################################################################################################################################
# INITALISE PANDAS DATAFRAMES

#Global pandas dataframe and output file to write to
_columns_mb = ['layer_id','mb_id','N_I','type_I','N_M','type_M','N_O','type_O','mu_hits','rms_hits']
_columns_hgcroc = ['layer_id','mb_id','wafer_u','wafer_v','type','partiality','density','mu_hgcroc0','rms_hgcroc0','mu_hgcroc1','rms_hgcroc1','mu_hgcroc2','rms_hgcroc2','mu_hgcroc3','rms_hgcroc3','mu_hgcroc4','rms_hgcroc4','mu_hgcroc5','rms_hgcroc5']
data_mb = pd.DataFrame( columns=_columns_mb )
data_hgcroc = pd.DataFrame( columns=_columns_hgcroc )


##############################################################################################################################################
# FUNCTION TO EXTRACT MODULE-MOTHERBOARD MAPPING INFORMATION FROM TEXT FILE PHILIPPE PROVIDED

def readMotherboardMap( fileName=os.environ['CMSSW_BASE']+"/src/analysis/data/motherboard_maps/mbmap_v9_allpartials.txt", layer_idx=1 ):

  #motherboard counter
  N_mb = 0
  #module counter
  N_mod = 0

  #open file to read from
  f_input = open( fileName, "r" )

  #define dict of to store info
  moduleMap = {}
  moduleMap_inverted = {}
  moduleSpecificationMap = {} #Map to store type of module for each moduleID
  motherboardMap = {}
  motherboardMap_inverted = {} #lists module co-ordinates for each motherboard
  motherboardCorrelationMap = {} #for each mb: lists id of neighbouring motherboards (no repeats i.e. if 1 has 2 as a neighbour, 2 does not have 1

  #Loop over lines in text file: i.e. each motherboard
  for line in f_input:
    motherboard_info = line.split(" ")
    #For lines in the specified layer...
    if( int(motherboard_info[0])+1 == layer_idx ):

      #Add one to motherboard counter
      N_mb += 1

      #loop over wafers connected to motherboard and add mapping to relevant dictionaries
      for wafer_idx in range(0, int(motherboard_info[3])):
        moduleMap["[%s,%s]"%(motherboard_info[4+2*wafer_idx],motherboard_info[5+2*wafer_idx])] = N_mod
        moduleMap_inverted[ N_mod ] = "[%s,%s]"%(motherboard_info[4+2*wafer_idx],motherboard_info[5+2*wafer_idx])
        moduleSpecificationMap[ N_mod ] = "%s:%s"%(motherboard_info[2][2*wafer_idx],motherboard_info[2][(2*wafer_idx)+1])
        motherboardMap[ int(moduleMap["[%s,%s]"%(motherboard_info[4+2*wafer_idx],motherboard_info[5+2*wafer_idx])]) ] = int( motherboard_info[1] )
        #Check if key in inverted MB map
        if N_mb in motherboardMap_inverted: motherboardMap_inverted[ N_mb ].append( "[%s,%s]"%(motherboard_info[4+2*wafer_idx],motherboard_info[5+2*wafer_idx]) )
        #If not create new list for key
        else: motherboardMap_inverted[ N_mb ] = ["[%s,%s]"%(motherboard_info[4+2*wafer_idx],motherboard_info[5+2*wafer_idx])]
        N_mod += 1

  #Loop over MBs, extract MBs physically next to given MB
  for mb_idx, module_list in motherboardMap_inverted.iteritems():

    #list to store neigbouring modules that are not in motherboard
    neighbourModulesId = []

    #Loop over modules in list
    for module in module_list:
      #Extract modules u and v co-ordinates
      module_uv = [int(module.split(",")[0][1:]),int(module.split(",")[1][:-1])]
      # If module exists, not in current motherboard and not already in list: then add to id to neighbourModulesId list
      if('[%g,%g]'%( module_uv[0]+1, module_uv[1] ) in moduleMap)&('[%g,%g]'%( module_uv[0]+1, module_uv[1] ) not in module_list ):
        if( moduleMap['[%g,%g]'%( module_uv[0]+1, module_uv[1])] not in neighbourModulesId ): neighbourModulesId.append( moduleMap[ '[%g,%g]'%( module_uv[0]+1, module_uv[1])]) #u+, v=
      if('[%g,%g]'%( module_uv[0]-1, module_uv[1] ) in moduleMap)&('[%g,%g]'%( module_uv[0]-1, module_uv[1] ) not in module_list ):
        if( moduleMap['[%g,%g]'%( module_uv[0]-1, module_uv[1])] not in neighbourModulesId ): neighbourModulesId.append( moduleMap[ '[%g,%g]'%( module_uv[0]-1, module_uv[1])]) #u-, v=
      if('[%g,%g]'%( module_uv[0], module_uv[1]+1 ) in moduleMap)&('[%g,%g]'%( module_uv[0], module_uv[1]+1 ) not in module_list ):
        if( moduleMap['[%g,%g]'%( module_uv[0], module_uv[1]+1)] not in neighbourModulesId ): neighbourModulesId.append( moduleMap[ '[%g,%g]'%( module_uv[0], module_uv[1]+1)]) #u=, v+
      if('[%g,%g]'%( module_uv[0], module_uv[1]-1 ) in moduleMap)&('[%g,%g]'%( module_uv[0], module_uv[1]-1 ) not in module_list ):
        if( moduleMap['[%g,%g]'%( module_uv[0], module_uv[1]-1)] not in neighbourModulesId ): neighbourModulesId.append( moduleMap[ '[%g,%g]'%( module_uv[0], module_uv[1]-1)]) #u=, v-
      if('[%g,%g]'%( module_uv[0]+1, module_uv[1]+1 ) in moduleMap)&('[%g,%g]'%( module_uv[0]+1, module_uv[1]+1 ) not in module_list ):
        if( moduleMap['[%g,%g]'%( module_uv[0]+1, module_uv[1]+1)] not in neighbourModulesId ): neighbourModulesId.append( moduleMap[ '[%g,%g]'%( module_uv[0]+1, module_uv[1]+1)]) #u+, v+
      if('[%g,%g]'%( module_uv[0]-1, module_uv[1]-1 ) in moduleMap)&('[%g,%g]'%( module_uv[0]-1, module_uv[1]-1 ) not in module_list ):
        if( moduleMap['[%g,%g]'%( module_uv[0]-1, module_uv[1]-1)] not in neighbourModulesId ): neighbourModulesId.append( moduleMap[ '[%g,%g]'%( module_uv[0]-1, module_uv[1]-1)]) #u-, v-

    #Define list to store id's of neighbouring motherboards
    neighbourMotherboardsId = []
    #loop of neighbouring modules
    for moduleId in neighbourModulesId:
      #if module is in motherboard map
      if moduleId in motherboardMap:
        #do not add reverse combination as would double on plots
        if motherboardMap[ moduleId ] not in motherboardCorrelationMap:
          #add neighbouring motherboards only once to list 
          if motherboardMap[ moduleId ] not in neighbourMotherboardsId: neighbourMotherboardsId.append( int(motherboardMap[ moduleId ]) )

    #Add to dictionary
    motherboardCorrelationMap[ mb_idx ] = sorted(neighbourMotherboardsId)

  return moduleMap, moduleMap_inverted, moduleSpecificationMap, motherboardMap, motherboardMap_inverted, motherboardCorrelationMap


##############################################################################################################################################
# FUNCTIONS TO ADD DATA TO PANDAS DATAFRAME FROM HISTOGRAMS

#Define function to extract relevant info from motherboard histogram file
def addMBinfo( mod_map, mod_spec_map, mb_imap, layer_idx=1 ):

  #Input histogram file
  fin_id = os.environ['CMSSW_BASE'] + "/src/analysis/output/hist_SiOnly_motherboard/HGCalOccupancy_SiOnly_layer%g.root"%layer_idx
  f_in = ROOT.TFile( fin_id )

  #Loop over motherboards and wafers n layer
  for mb_idx, wafers in mb_imap.iteritems():
    #save information to add to DataFrame
    if shiftLayer: _layer = layer_idx-1
    else: _layer = layer_idx
    _id = mb_idx
    #extract number and type of wafers
    N_imo = [0,0,0]
    type_imo = ["","",""]
    for wafer in wafers:
      wafer_type = mod_spec_map[mod_map[ wafer ]].split(":")[1]
      if( wafer_type == "I" ):
        N_imo[0] += 1
        type_imo[0] += mod_spec_map[mod_map[ wafer ]].split(":")[0]
      elif( wafer_type == "M" ):
        N_imo[1] += 1
        type_imo[1] += mod_spec_map[mod_map[ wafer ]].split(":")[0]
      else:
        N_imo[2] += 1
        type_imo[2] += mod_spec_map[mod_map[ wafer ]].split(":")[0]
    # if no wafers of a given type then set type to -
    for type_ in range(len(type_imo)):
      if type_imo[ type_ ]  == "": type_imo[type_] = "-" 
    #extract mean and rms values from histogram
    hist_mb = f_in.Get( "h_mb%g"%mb_idx )
    mb_mean = hist_mb.GetMean()
    mb_rms = hist_mb.GetRMS()

    #Add output to pandas dataFrame
    data_mb.loc[ len(data_mb) ] = [_layer,_id,N_imo[0],type_imo[0],N_imo[1],type_imo[1],N_imo[2],type_imo[2],mb_mean,mb_rms]



#Define function to extract relevant info from hgcroc histogram file
def addHGCROCinfo( mod_map, mod_spec_map, mb_imap, layer_idx=1 ):

  #Input histogram file
  fin_id = os.environ['CMSSW_BASE'] + "/src/analysis/output/hist_SiOnly_hgcroc/HGCalOccupancy_SiOnly_hgcroc_layer%g.root"%layer_idx
  #fin_id = os.environ['CMSSW_BASE'] + "/src/analysis/output/sandbox_output/test_layer1_1.root"
  f_in = ROOT.TFile( fin_id )

  #Loop over motherboards and wafers in layer
  for mb_idx, wafers in mb_imap.iteritems():
    for wafer in wafers:
      #save information to add to dataframe
      if shiftLayer: _layer = layer_idx-1
      else: _layer = layer_idx
      _mb = mb_idx
      #get wafer info
      _wafer_uv = [wafer.split(",")[0][1:],wafer.split(",")[1][:-1]]
      _type = mod_spec_map[mod_map[ wafer ]].split(":")[1]
      _partiality = mod_spec_map[mod_map[ wafer ]].split(":")[0]
      if( _type == "M" )|( _type == "O" ): _density = "low"
      else: _density = "high"
      #for low density wafers skip hgcroc 4,5 and 6
      _mean_hgcroc = [-1,-1,-1,-1,-1,-1]
      _rms_hgcroc = [-1,-1,-1,-1,-1,-1]
      if( _density == "low" ): upperRocRange = 3
      else: upperRocRange = 6
      for _roc in range(0,upperRocRange):
        hist_hgcroc = f_in.Get( "h_mod%g_hgcroc%g"%(mod_map[wafer],_roc) )
        _mean_hgcroc[_roc] = hist_hgcroc.GetMean()
        _rms_hgcroc[_roc] = hist_hgcroc.GetRMS()

      #Add wafer info to pandas dataFrame
      data_hgcroc.loc[ len(data_hgcroc) ] = [_layer,_mb,int(_wafer_uv[0]),int(_wafer_uv[1]),_type,_partiality,_density,_mean_hgcroc[0],_rms_hgcroc[0],_mean_hgcroc[1],_rms_hgcroc[1],_mean_hgcroc[2],_rms_hgcroc[2],_mean_hgcroc[3],_rms_hgcroc[3],_mean_hgcroc[4],_rms_hgcroc[4],_mean_hgcroc[5],_rms_hgcroc[5]]


##############################################################################################################################################
# PRINTING FUNCTIONS

#Function to write motherboard data to text file
def printMBInfo( printToScreen=False ):
  fout_id = os.environ['CMSSW_BASE'] + "/src/analysis/output/data/motherboard/ascii/HGCalOccupancy_SiOnly_motherboard.txt"
  fout = open( fout_id, "w" )
  for layer_idx in range(0,36):
    _data = data_mb[ data_mb['layer_id'] == layer_idx ]
    fout.write("L %g %g\n"%(layer_idx,len(_data)))
    if( printToScreen ): print "L %g %g"%(layer_idx,len(_data))
    for mb_idx in range(0,len(_data)):
      _mb = _data.iloc[ mb_idx ]
      fout.write("M %g %g %s %g %s %g %s %4.2f %4.2f\n"%(_mb['mb_id'],_mb['N_I'],_mb['type_I'],_mb['N_M'],_mb['type_M'],_mb['N_O'],_mb['type_O'], _mb['mu_hits'], _mb['rms_hits']))
      if( printToScreen ): print "M %g %g %s %g %s %g %s %4.2f %4.2f"%(_mb['mb_id'],_mb['N_I'],_mb['type_I'],_mb['N_M'],_mb['type_M'],_mb['N_O'],_mb['type_O'], _mb['mu_hits'], _mb['rms_hits'])
  #close output file
  fout.close()


#Function to write hgcroc data to text file
def printHGCROCInfo( printToScreen=False ):
  fout_id = os.environ['CMSSW_BASE'] + "/src/analysis/output/data/hgcroc/ascii/HGCalOccupancy_SiOnly_hgcroc.txt"
  fout = open( fout_id, "w" )
  for layer_idx in range(0,36):

    _data = data_hgcroc[ data_hgcroc['layer_id'] == layer_idx ]
    fout.write("L %g %g\n"%(layer_idx,len(_data)))
    if( printToScreen ): print "L %g %g"%(layer_idx,len(_data))

    for wafer_idx in range(0,len(_data)):
      _wafer = _data.iloc[ wafer_idx ]
      #for low density wafers
      if _wafer['density'] == "low":
        fout.write("W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f\n"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2']))
        if( printToScreen ): print "W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2'])
      #for high density wafers
      else:
        fout.write("W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f 3 %4.2f %4.2f 4 %4.2f %4.2f 5 %4.2f %4.2f\n"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2'],_wafer['mu_hgcroc3'],_wafer['rms_hgcroc3'],_wafer['mu_hgcroc4'],_wafer['rms_hgcroc4'],_wafer['mu_hgcroc5'],_wafer['rms_hgcroc5']))
        if( printToScreen ): print "W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f 3 %4.2f %4.2f 4 %4.2f %4.2f 5 %4.2f %4.2f"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2'],_wafer['mu_hgcroc3'],_wafer['rms_hgcroc3'],_wafer['mu_hgcroc4'],_wafer['rms_hgcroc4'],_wafer['mu_hgcroc5'],_wafer['rms_hgcroc5']) 

  #close output file
  fout.close() 


#function to write all info to text file
def printAllInfo( printToScreen=False ):
  fout_id = os.environ['CMSSW_BASE'] + "/src/analysis/output/data/total/ascii/HGCalOccupancy_SiOnly.txt"
  fout = open( fout_id, "w" )
  for layer_idx in range(0,36):

    _dataMB = data_mb[ data_mb['layer_id'] == layer_idx ]
    _dataHGCROC = data_hgcroc[ data_hgcroc['layer_id'] == layer_idx ]
    fout.write("L %g %g\n"%(layer_idx,len(_dataMB)))
    if( printToScreen ): print "L %g %g"%(layer_idx,len(_dataMB))

    for mb_idx in range(0,len(_dataMB)):
      _mb = _dataMB.iloc[ mb_idx ]
      fout.write("M %g %g %s %g %s %g %s %4.2f %4.2f\n"%(_mb['mb_id'],_mb['N_I'],_mb['type_I'],_mb['N_M'],_mb['type_M'],_mb['N_O'],_mb['type_O'], _mb['mu_hits'], _mb['rms_hits']))
      if( printToScreen ): print "M %g %g %s %g %s %g %s %4.2f %4.2f"%(_mb['mb_id'],_mb['N_I'],_mb['type_I'],_mb['N_M'],_mb['type_M'],_mb['N_O'],_mb['type_O'], _mb['mu_hits'], _mb['rms_hits'])
      #get data of wafers in  motherboard
      _data = _dataHGCROC[ _dataHGCROC['mb_id'] == _mb['mb_id']]  

      for wafer_idx in range(0,len(_data)):
        _wafer = _data.iloc[ wafer_idx ]
        #for low density wafers
        if _wafer['density'] == "low":
          fout.write("W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f\n"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2']))
          if( printToScreen ): print "W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2'])
        #for high density wafers
        else:
          fout.write("W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f 3 %4.2f %4.2f 4 %4.2f %4.2f 5 %4.2f %4.2f\n"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2'],_wafer['mu_hgcroc3'],_wafer['rms_hgcroc3'],_wafer['mu_hgcroc4'],_wafer['rms_hgcroc4'],_wafer['mu_hgcroc5'],_wafer['rms_hgcroc5']))
          if( printToScreen ): print "W M%g (%g,%g) %s %s %s 0 %4.2f %4.2f 1 %4.2f %4.2f 2 %4.2f %4.2f 3 %4.2f %4.2f 4 %4.2f %4.2f 5 %4.2f %4.2f"%(_wafer['mb_id'],_wafer['wafer_u'],_wafer['wafer_v'],_wafer['partiality'],_wafer['type'],_wafer['density'],_wafer['mu_hgcroc0'],_wafer['rms_hgcroc0'],_wafer['mu_hgcroc1'],_wafer['rms_hgcroc1'],_wafer['mu_hgcroc2'],_wafer['rms_hgcroc2'],_wafer['mu_hgcroc3'],_wafer['rms_hgcroc3'],_wafer['mu_hgcroc4'],_wafer['rms_hgcroc4'],_wafer['mu_hgcroc5'],_wafer['rms_hgcroc5'])

  #close output file
  fout.close()

##############################################################################################################################################

#Main body of script: extract information from histograms in each layer

for hgcLayer in range(1,37): #note layers defined in root files are not shifted

  #Read mapping to get info of layer
  module_map, module_imap, module_specification_map, motherboard_map, motherboard_imap, motherboard_correlation_map = readMotherboardMap( layer_idx = hgcLayer )

  #add info to dataframes
  addMBinfo( module_map, module_specification_map, motherboard_imap, layer_idx = hgcLayer )
  addHGCROCinfo( module_map, module_specification_map, motherboard_imap, layer_idx = hgcLayer )


##############################################################################################################################################
# WRITING OUT DATA

#Write out data to text file
printMBInfo( printToScreen=False )
printHGCROCInfo( printToScreen=False )
printAllInfo( printToScreen=False )

#Save pandas DataFrame as csv and pkl
pd.to_pickle( data_mb, os.environ['CMSSW_BASE']+"/src/analysis/output/data/motherboard/pkl/HGCalOccupancy_SiOnly_motherboard.pkl" )
data_mb.to_csv( os.environ['CMSSW_BASE']+"/src/analysis/output/data/motherboard/csv/HGCalOccupancy_SiOnly_motherboard.csv" )
pd.to_pickle( data_hgcroc, os.environ['CMSSW_BASE']+"/src/analysis/output/data/hgcroc/pkl/HGCalOccupancy_SiOnly_hgcroc.pkl" )
data_hgcroc.to_csv( os.environ['CMSSW_BASE']+"/src/analysis/output/data/hgcroc/csv/HGCalOccupancy_SiOnly_hgcroc.csv" )

##############################################################################################################################################

