import ROOT
import pandas as pd
import sys
import os
import math
from array import array
from sets import Set
from optparse import OptionParser

# First check with new files: running over one ttbar
# Change to TChain adding all ttbar ntuples
verbose = False

def get_options():
  parser = OptionParser()
  parser = OptionParser( usage="usage: python HGCal_occupancy_Analyzer.py <INPUT NTUP> <MAX EVENTS> <LAYER IDX>" )
  parser.add_option("-i", "--input", dest="fileID", default='', help="Input ntuple file number")
  parser.add_option("-n", "--maxEvents", dest="maxEvents", default=-1, help="Maximum number of events")
  parser.add_option("-l", "--layer", dest="hgcLayer", default=1, help="HGCal Layer")
  return parser.parse_args()

(opt,args) = get_options()

#Extract file from /dat/ folder
fin_id = os.environ['CMSSW_BASE'] + "/src/analysis/ntuples/ttbar_14TeV_D28_200PU/ttbar_14TeV_D28_200PU_" + opt.fileID + ".root"
fileID = int( opt.fileID )
maxEvents = int( opt.maxEvents )
hgcLayer = int( opt.hgcLayer )

#Only working in HGCalEE (for now): therefore require layer number 1-28
if( hgcLayer > 36 ):
  print "Error: only considering Si only layers, layer in [1,36]"
  sys.exit(1)

print "\n~~~~~~~~~~~~~~~~~"
print " HGCAL Occupancy Analysis: HGCROC"
print "\n~~~~~ Input ~~~~~"
print "  * Accessing input file: %s"%fin_id
print "  * Max Events = %g"%maxEvents
print "  * HGCal Layer = %g"%hgcLayer
print ""

#Open tree to read from
fin = ROOT.TFile( fin_id )
tree = fin.Get("ana/hgc")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Function to read motherboard and modules into dictionary and return number of motherboards/modules for chosen layer
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
 
  return N_mod, moduleMap, moduleMap_inverted, moduleSpecificationMap, N_mb, motherboardMap, motherboardMap_inverted, motherboardCorrelationMap

#Read mapping to get info of layer
N_modules, module_map, module_imap, module_specification_map, N_motherboards, motherboard_map, motherboard_imap, motherboard_correlation_map = readMotherboardMap( layer_idx = hgcLayer )
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#Define dictionary for detector id to name
hgcDetDict = {8:'HGCalEE',9:'HGCalHSi',10:'HGCalHSc'}

#Define wafer width
hgcWaferWidth = 20.32

#Offsets and masks for: HGCal
hgcDetOffset = 28
hgcDetMask = 0xF
hgcTypeOffset = 26
hgcTypeMask = 0x3
hgcZOffset = 25
hgcZMask = 0x1
#HGCSilicon
hgcSiliconLayerOffset = 20
hgcSiliconLayerMask = 0x1F
hgcSiliconWaferVSignOffset = 19
hgcSiliconWaferVSignMask = 0x1
hgcSiliconWaferVOffset = 15
hgcSiliconWaferVMask = 0xF
hgcSiliconWaferUSignOffset = 14
hgcSiliconWaferUSignMask = 0x1
hgcSiliconWaferUOffset = 10
hgcSiliconWaferUMask = 0xF
hgcSiliconCellVOffset = 5
hgcSiliconCellVMask = 0x1F
hgcSiliconCellUMask = 0x1F
#HGCScintillator
hgcScintLayerOffset = 17
hgcScintLayerMask = 0x1F
hgcScintRadiusOffset = 9
hgcScintRadiusMask = 0xFF
hgcScintPhiMask = 0x1FF

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Functions for analysis: related to hits
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Return #hits for event
def Nhits( _event ): return len(_event.rechit_detid)

#Return true if in Silicon/Scintillator
def isSilicon( _event, _hit ):
  _detid = _event.rechit_detid[_hit]
  if (_detid>>hgcDetOffset)&hgcDetMask in [8,9]: return True
  else: return False
def isScint( _event, _hit ):
  _detid = _event.rechit_detid[_hit]
  if (_detid>>hgcDetOffset)&hgcDetMask == 10: return True
  else: return False

#Return true if in EE/HSi/HSc
def inHGCalEE( _hit ): 
  if _hit.det() == 8: return True
  else: return False
def inHGCalHSi( _hit ): 
  if _hit.det() == 9: return True
  else: return False
def inHGCalHSc( _hit ): 
  if _hit.det() == 10: return True
  else: return False

#Return int depending on cassette
def cassetteID_EE( rechitEE ):
  if( rechitEE.waferv()>= 0 )&( rechitEE.waferu()<=-1  ): return 0
  elif( rechitEE.waferv()<=-1 )&( rechitEE.waferu()<=rechitEE.waferv() ): return 1
  elif( rechitEE.waferu()<=0 )&( rechitEE.waferu()>rechitEE.waferv() ): return 2
  elif( rechitEE.waferv()<=0 )&( rechitEE.waferu()>0 ): return 3
  elif( rechitEE.waferv()>0 )&( rechitEE.waferu()>=rechitEE.waferv() ): return 4
  elif( rechitEE.waferu()>=0 )&( rechitEE.waferu()<rechitEE.waferv() ): return 5
  else: return 6

#Function to map wafer to wafer in cassette 0
def wafer_mapping_to_cass0( wafer, cassetteID ):
  if( cassetteID == 0 ): return [wafer[0],wafer[1]]
  elif( cassetteID == 1 ): return [wafer[1],wafer[1]-wafer[0]]
  elif( cassetteID == 2 ): return [wafer[1]-wafer[0],-1*wafer[0]]
  elif( cassetteID == 3 ): return [-1*wafer[0],-1*wafer[1]]
  elif( cassetteID == 4 ): return [-1*wafer[1],-1*wafer[1]+wafer[0]]
  elif( cassetteID == 5 ): return [-1*wafer[1]+wafer[0],wafer[0]]

#Return int depending on wafer + cassette + z (waferID)
def moduleID_EE( wafer, cassetteID ):
  #Add check to catch rechits which do not have a module ID in the map
  if '[%g,%g]'%(wafer_mapping_to_cass0(wafer,cassetteID)[0],wafer_mapping_to_cass0(wafer,cassetteID)[1]) in module_map.keys():
    if( cassetteID == 0 ): return module_map[ '[%g,%g]'%(wafer[0],wafer[1]) ]
    elif( cassetteID == 1 ): return module_map[ '[%g,%g]'%(wafer[1],wafer[1]-wafer[0]) ]
    elif( cassetteID == 2 ): return module_map[ '[%g,%g]'%(wafer[1]-wafer[0],-1*wafer[0]) ]
    elif( cassetteID == 3 ): return module_map[ '[%g,%g]'%(-1*wafer[0],-1*wafer[1]) ]
    elif( cassetteID == 4 ): return module_map[ '[%g,%g]'%(-1*wafer[1],-1*wafer[1]+wafer[0]) ]
    elif( cassetteID == 5 ): return module_map[ '[%g,%g]'%(-1*wafer[1]+wafer[0],wafer[0]) ]
  else: return -1

#Return int to label HGCROC: depending on cell number and what wafer (low density/high density) and cassette
def hgcrocID_EE( cell, moduleID, cassetteID ):
  #extract density of module from moduleID: format = "Partiality:Density"
  if( module_specification_map[moduleID].split(":")[1] == "M" )|( module_specification_map[moduleID].split(":")[1] == "O" ): moduleDensity = "low"
  else: moduleDensity = "high"

  hgcroc_id = -1

  #for low density wafer: 3 hgcrocs per module
  if moduleDensity == "low":
    #for even-numbered cassettes
    if( cassetteID % 2 == 0 ):
      #extract nominal hgcroc from cell u and v co-ordinates as if in cassette 0
      if( cell[0] < 8 )&( cell[1] < 8 ): hgcroc_id = 0
      elif( cell[0] > cell[1] ): hgcroc_id = 1
      else: hgcroc_id = 2
      #rotate HGCROC numbering to map to cassette 0
      if( cassetteID == 2 ): hgcroc_id = (hgcroc_id+2)%3
      elif( cassetteID == 4 ): hgcroc_id = (hgcroc_id+1)%3
    #for odd numbered cassettes
    else:
      #extract nominal hgcroc number from cell u and v co-ordinates as if in cassette 5
      if( cell[0] >= 8 )&( cell[1] >= 8 ): hgcroc_id = 2
      elif( cell[0] > cell[1] ): hgcroc_id = 1
      else: hgcroc_id = 0
      #rotate hgcroc numbering to map to cassette 5
      if( cassetteID == 3 ): hgcroc_id = (hgcroc_id+1)%3
      elif( cassetteID == 1 ): hgcroc_id = (hgcroc_id+2)%3

  #for high density wafer: 6 hgcrocs per module
  elif moduleDensity == "high":
    #for even-numbering cassettes:
    if( cassetteID % 2 == 0 ):
      #define hgcroc numbers for cassette 0
      if( cell[0] < 6 )&( cell[1] < 12 ): hgcroc_id = 0
      elif( cell[0] < 12 )&( cell[1] < 12 ): hgcroc_id = 3
      elif( cell[0] > (cell[1]+6)): hgcroc_id = 1
      elif( cell[0] > cell[1] ): hgcroc_id = 4
      elif( cell[1] >= 18 ): hgcroc_id = 2
      else: hgcroc_id = 5
      #rotate hgcroc numbering to match cassette 0 (0->1->2->0 and 3->4->5->3)
      if( cassetteID == 2 ):
        if( hgcroc_id < 3 ): hgcroc_id = (hgcroc_id+2)%3
        else: hgcroc_id = (((hgcroc_id-3)+2)%3)+3
      elif( cassetteID == 4 ):
        if( hgcroc_id < 3 ): hgcroc_id = (hgcroc_id+1)%3
        else: hgcroc_id = (((hgcroc_id-3)+1)%3)+3 
    #for odd numbered cassettes
    else:
      #define hgcroc numbers for cassette 5
      if( cell[0] >= 18 )&( cell[1] >= 12 ): hgcroc_id = 2
      elif( cell[0] >= 12 )&( cell[1] >= 12 ): hgcroc_id = 5
      elif( cell[0] > cell[1] )&( cell[1] < 6 ): hgcroc_id = 1
      elif( cell[0] > cell[1] ): hgcroc_id = 4
      elif( cell[1] >= (cell[0]+6) ): hgcroc_id = 0
      else: hgcroc_id = 3
      #rotate hgcroc numbering to match cassette 5 scheme (0->1->2->0 and 3->4->5->3)
      if( cassetteID == 3 ):
        if( hgcroc_id < 3 ): hgcroc_id = (hgcroc_id+1)%3
        else: hgcroc_id = (((hgcroc_id-3)+1)%3)+3
      elif( cassetteID == 1 ):
        if( hgcroc_id < 3 ): hgcroc_id = (hgcroc_id+2)%3
        else: hgcroc_id = (((hgcroc_id-3)+2)%3)+3

  #print " > cell = (%g,%g), cassette = %g, wafer = %s, specification = %s, density = %s, hgcrocID = %g"%(cell[0],cell[1],cassetteID,module_imap[moduleID],module_specification_map[moduleID],moduleDensity,hgcroc_id)
  return hgcroc_id
  

#Return int depending on motherboard: motherboards for each layer in EE
def motherboardID_EE( _moduleID, _motherboard_map ):
  return _motherboard_map[ _moduleID ]

#Function to return quantile for given histogram
def findQuantile( hist, xq ):
  N_quantiles = 100
  x_quantiles = []
  for i in range(0,N_quantiles): x_quantiles.append( float(i+1)/N_quantiles )
  x_quantiles_arr = array('d', x_quantiles )
  y_quantiles_arr = array('d', [0]*N_quantiles )
  #Determine quantiles
  hist.GetQuantiles( N_quantiles, y_quantiles_arr, x_quantiles_arr )
  #Find idx corresponding to position of quantiles want to extract
  x_idx = -1
  for i in range( len(x_quantiles) ):
    if x_quantiles[i] == xq: return y_quantiles_arr[i]
  #if not found return -1
  return -1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Classes for reco hits in the HGCAL
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Define class of rechit in Silicon detector
class RecHitSilicon:

  #Constructor method: takes detid and energy as input
  def __init__(self, _event, _hit):
    _detid = _event.rechit_detid[_hit]
    _energy = _event.rechit_energy[_hit]
    self.HitIdx = _hit
    self.Detector = (_detid>>hgcDetOffset)&hgcDetMask
    self.Type = (_detid>>hgcTypeOffset)&hgcTypeMask
    if( (_detid>>hgcZOffset)&hgcZMask == 0 ): self.Zside = 1
    else: self.Zside = -1
    #if in HGCalHSi then add 28 (number of layers in EE) to layer
    if( (_detid>>hgcDetOffset)&hgcDetMask == 9 ): self.Layer = ((_detid>>hgcSiliconLayerOffset)&hgcSiliconLayerMask)+28
    else: self.Layer = (_detid>>hgcSiliconLayerOffset)&hgcSiliconLayerMask
    if( (_detid>>hgcSiliconWaferVSignOffset)&hgcSiliconWaferVSignMask == 0 ): waferV = (_detid>>hgcSiliconWaferVOffset)&hgcSiliconWaferVMask
    else: waferV = -1*((_detid>>hgcSiliconWaferVOffset)&hgcSiliconWaferVMask)
    if( (_detid>>hgcSiliconWaferUSignOffset)&hgcSiliconWaferUSignMask == 0 ): waferU = (_detid>>hgcSiliconWaferUOffset)&hgcSiliconWaferUMask
    else: waferU = -1*((_detid>>hgcSiliconWaferUOffset)&hgcSiliconWaferUMask)
    self.Wafer = [waferU,waferV]
    self.Cell = [_detid&hgcSiliconCellUMask,(_detid>>hgcSiliconCellVOffset)&hgcSiliconCellVMask]
    self.Energy = _energy
    self.x = _event.rechit_x[_hit]
    self.y = _event.rechit_y[_hit]

  #member functions to extract info
  def det(self): return self.Detector
  def siltype(self): return self.Type
  def Z(self): return self.Zside
  def layer(self): return self.Layer
  def wafer(self): return self.Wafer
  def waferu(self): return self.Wafer[0]
  def waferv(self): return self.Wafer[1]
  def waferx(self): return -2*self.Wafer[0]+self.Wafer[1]
  def wafery(self): return ((3**0.5)/2)*self.Wafer[1]
  def cell(self): return self.Cell
  def cellu(self): return self.Cell[0]
  def cellv(self): return self.Cell[1]
  def E(self): return self.Energy
  def X(self): return self.x
  def Y(self): return self.y
  #functions to return cassetteID/moduleID/motherboardID of hit
  def cassetteID(self): return cassetteID_EE(self)
  def moduleID(self): return moduleID_EE( self.Wafer, cassetteID_EE(self) )
  def hgcrocID(self): return hgcrocID_EE( self.Cell, self.moduleID(), self.cassetteID() )
  def motherboardID(self): return motherboardID_EE( self.moduleID(), motherboard_map )
  def x0(self): return x_cassette0( self )
  def y0(self): return y_cassette0( self )
  
  #member function to print info
  def Print(self): print "Hit %g ::: Det = %s, Type = %g, Z = %g, Layer = %g, Wafer = (%g,%g), Cell = (%g,%g), Energy = %5.4f"%(self.HitIdx,hgcDetDict[self.Detector],self.Type,self.Zside,self.Layer,self.Wafer[0],self.Wafer[1],self.Cell[0],self.Cell[1],self.Energy)  

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Define class of rechit in Scintillator detector
class RecHitScint:

  #Constructor method: takes detid and energy as input
  def __init__(self, _event, _hit):
    _detid = _event.rechit_detid[_hit]
    _energy = _event.rechit_energy[_hit]
    self.HitIdx = _hit
    self.Detector = (_detid>>hgcDetOffset)&hgcDetMask
    self.Type = (_detid>>hgcTypeOffset)&hgcTypeMask
    if( (_detid>>hgcZOffset)&hgcZMask == 0 ): self.Zside = 1
    else: self.Zside = -1
    #in HGCalHSc therefore add 28 (number of layers in EE) to layer
    self.Layer = ((_detid>>hgcScintLayerOffset)&hgcScintLayerMask)+28
    self.Radius = (_detid>>hgcScintRadiusOffset)&hgcScintRadiusMask
    self.Phi = _detid&hgcScintPhiMask
    self.Energy = _energy

  #member functions to extract info
  def det(self): return self.Detector
  def sctype(self): return self.Type
  def Z(self): return self.Zside
  def layer(self): return self.Layer
  def R(self): return self.Radius
  def Phi(self): return self.Phi
  def E(self): return self.Energy

  #member function to print info
  def Print(self): print "Hit %g ::: Det = %s, Type = %g, Z = %g, Layer = %g, iRadius = %g, iPhi = %g, Energy = %5.4f"%(self.HitIdx,hgcDetDict[self.Detector],self.Type,self.Zside,self.Layer,self.Radius,self.Phi,self.Energy)  

################################################################################################
#Output root file: histograms etc
fout_id = os.environ['CMSSW_BASE']+'/src/analysis/output/hist_SiOnly_hgcroc/lay%g/HGCalOccupancy_SiOnly_hgcroc_layer%g_%g.root'%(hgcLayer,hgcLayer,fileID)
fout = ROOT.TFile( fout_id, "RECREATE" )

#Define histograms
histDict_hgcroc = {}
for mod_idx in module_imap:
  #extract density of module: for low density modules (M/O) save 3 hgcroc histograms
  if( module_specification_map[mod_idx].split(":")[1] == "M" )|( module_specification_map[mod_idx].split(":")[1] == "O" ):
    for hgcroc_idx in range(0,3):
      histDict_hgcroc[ 'mod%g_hgcroc%g'%(mod_idx,hgcroc_idx) ] = ROOT.TH1F("h_mod%g_hgcroc%g"%(mod_idx,hgcroc_idx),"Number of hits in wafer=%s (%s), hgcroc=%g, layer = %g"%(module_imap[mod_idx],module_specification_map[mod_idx],hgcroc_idx,hgcLayer),100,0,100)
  #for high density wafers (I) save 6 hgcroc histograms
  else:
    for hgcroc_idx in range(0,6):
      histDict_hgcroc[ 'mod%g_hgcroc%g'%(mod_idx,hgcroc_idx) ] = ROOT.TH1F("h_mod%g_hgcroc%g"%(mod_idx,hgcroc_idx),"Number of hits in wafer=%s (%s), hgcroc=%g, layer = %g"%(module_imap[mod_idx],module_specification_map[mod_idx],hgcroc_idx,hgcLayer),100,0,100)

#COUNTER HISTOGRAMS: reset after each event
#Count number of hits in each (cassette,+-z) combination in bins of histogram: different histogram for each hgcroc
counterHist_hgcroc = {}
for mod_idx in module_imap:
  #low density modules...
  if( module_specification_map[mod_idx].split(":")[1] == "M" )|( module_specification_map[mod_idx].split(":")[1] == "O" ):
    for hgcroc_idx in range(0,3):
      counterHist_hgcroc[ 'nhits_mod%g_hgcroc%g'%(mod_idx,hgcroc_idx) ] = ROOT.TH1F( "h_nhits_mod%g_hgcroc%g"%(mod_idx,hgcroc_idx),"",12,0,12)
  #for high density modules...
  else:
    for hgcroc_idx in range(0,6):
      counterHist_hgcroc[ 'nhits_mod%g_hgcroc%g'%(mod_idx,hgcroc_idx) ] = ROOT.TH1F( "h_nhits_mod%g_hgcroc%g"%(mod_idx,hgcroc_idx),"",12,0,12)

################################################################################################
#Loop over events in NTUP
eventCounter = 0

for event in tree:

  if eventCounter == maxEvents: break

  if( maxEvents < tree.GetEntries() )&( maxEvents > 0 ): print "Processing event: %g/%g"%(eventCounter,maxEvents-1)
  else: print "Processing event: %g/%g"%(eventCounter,tree.GetEntries()-1)

  #Loop over hits in event
  for hit_idx in range(0, Nhits(event) ):

    #For hits in the silicon wafers
    if( isSilicon( event, hit_idx ) ):
      hit = RecHitSilicon( event, hit_idx )
      #Hits in EE or HE(Si only)
      if( inHGCalEE( hit ) )|( inHGCalHSi( hit ) ):
        #Hits in specified layer: hgcLayer
        if( hit.layer() == hgcLayer ):
          #+z endcap
          if( hit.Z() == 1 ):

            #determine cassette of hit
            cassette = hit.cassetteID() 
            #determine moduleID of hit
            module = hit.moduleID() 
            #CHECK::: if module exists in layer then add hit to module counter
            if module == -1: 
              if verbose: print "Event %g --> HIT ERROR: module [%g,%g] not in module map for layer %g"%(eventCounter,wafer_mapping_to_cass0(hit.wafer(),cassette)[0],wafer_mapping_to_cass0(hit.wafer(),cassette)[1],hgcLayer) 
            else:
              #determine hgcrocID of hit
              hgcroc = hit.hgcrocID()
              #fill counter histogram (using cassette number)
              if hgcroc == -1: print "Event %g --> HIT ERROR: hgcroc not defined"
              else: counterHist_hgcroc[ 'nhits_mod%g_hgcroc%g'%(module,hgcroc) ].Fill( cassette )
 
              #determine motherboardID of hit
              motherboard = hit.motherboardID()
       
          #-z endcap
          elif( hit.Z() == -1 ):

            #determine cassette of hit: add six when filling histograms as filling negz
            cassette = hit.cassetteID() 
            #determine moduleID of hit
            module = hit.moduleID() 
            #CHECK::: if module exists in layer then add hit to module counter
            if module == -1: 
              if verbose: print "Event %g --> HIT ERROR: module [%g,%g] not in module map for layer %g"%(eventCounter,wafer_mapping_to_cass0(hit.wafer(),cassette)[0],wafer_mapping_to_cass0(hit.wafer(),cassette)[1],hgcLayer)
            else:
              #determine hgcrocID of hit
              hgcroc = hit.hgcrocID()
              #fill counter histogram (using cassette number + 6 (for negz))
              if hgcroc == -1: print "Event %g --> HIT ERROR: hgcroc not defined"
              else: counterHist_hgcroc[ 'nhits_mod%g_hgcroc%g'%(module,hgcroc) ].Fill( cassette+6 )

              #determine motherboardID of hit
              motherboard = hit.motherboardID()

    #For hits in the scintillator panels
    #if( isScint( event, hit_idx ) ):

  # End of rechits loop

  # Fill hit distributions with bin contents from counter histograms
  for mod_idx in module_imap:
    #low density modules...
    if( module_specification_map[mod_idx].split(":")[1] == "M" )|( module_specification_map[mod_idx].split(":")[1] == "O" ):
      for hgcroc_idx in range(0,3): 
        for _bin in range(1,counterHist_hgcroc['nhits_mod%g_hgcroc%g'%(mod_idx,hgcroc_idx)].GetNbinsX()+1): histDict_hgcroc['mod%g_hgcroc%g'%(mod_idx,hgcroc_idx)].Fill( counterHist_hgcroc['nhits_mod%g_hgcroc%g'%(mod_idx,hgcroc_idx)].GetBinContent( _bin ))
    #for high density modules...
    else:
      for hgcroc_idx in range(0,6):
        for _bin in range(1,counterHist_hgcroc['nhits_mod%g_hgcroc%g'%(mod_idx,hgcroc_idx)].GetNbinsX()+1): histDict_hgcroc['mod%g_hgcroc%g'%(mod_idx,hgcroc_idx)].Fill( counterHist_hgcroc['nhits_mod%g_hgcroc%g'%(mod_idx,hgcroc_idx)].GetBinContent( _bin ))

  # Reset counter histograms
  for counterHist in counterHist_hgcroc.itervalues(): counterHist.Reset()
  
  #Add to event counter
  eventCounter +=1

#End of events loop
  
################################################################################################
#Delete counter histograms so they are not saved to file
for counterHist in counterHist_hgcroc.itervalues(): counterHist.Delete()
################################################################################################
#Close root file to write to
fout.Write()
fout.Close()
