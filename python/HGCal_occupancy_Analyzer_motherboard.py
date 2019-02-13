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
print " HGCAL Occupancy Analysis: motherboard"
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
 
  return N_mod, moduleMap, moduleMap_inverted, N_mb, motherboardMap, motherboardMap_inverted, motherboardCorrelationMap

#Read mapping to get info of layer
N_modules, module_map, module_imap, N_motherboards, motherboard_map, motherboard_imap, motherboard_correlation_map = readMotherboardMap( layer_idx = hgcLayer )
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

#Return int depending on motherboard: motherboards for each layer in EE
def motherboardID_EE( _moduleID, _motherboard_map ):
  return _motherboard_map[ _moduleID ]

#Return (x0,y0): x and y co-ordinates mapped onto cassette-0
#def x_cassette0( rechitEE ):
#  x = rechitEE.X()
#  #get x-co-ordinate of wafer centre
#  x_c = rechitEE.waferx()
#  #x localised wafer position
#  x_local = x-x_c
#
#  #Find corresponding wafer in cassette0: x co-ordinate
#  module = rechitEE.moduleID()
#  module_uv = module_imap[ module ]
#  print "Hit::: Wafer = %s, cassette = %g, x_hit = %4.2f, x_wafer = %4.2f, x_local = %4.2f, module = %g, wafer0 = %s"%(rechitEE.wafer(),rechitEE.cassetteID(),x,x_c,x_local,module,module_uv) 

#def y_cassette0( rechitEE ):
#  y = rechitEE.Y()
#  #get y-co-ordinate of wafer centre
#  y_c = rechitEE.wafery()
#  #x localised wafer position
#  y_local = y-y_c
#
#  #Find corresponding wafer in cassette0: y co-ordinate
#  module = rechitEE.moduleID()
#  module_uv = module_imap[ module ]
#  print "Hit::: Wafer = %s, cassette = %g, y_hit = %4.2f, y_wafer = %4.2f, y_local = %4.2f, module = %g, wafer0 = %s"%(rechitEE.wafer(),rechitEE.cassetteID(),y,y_c,y_local,module,module_uv)


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
#fout_id = os.environ['CMSSW_BASE']+'/src/analysis/output/hist_SiOnly_motherboard/lay%g/HGCalOccupancy_SiOnly_layer%g_%g.root'%(hgcLayer,hgcLayer,fileID)
fout_id = os.environ['CMSSW_BASE']+'/src/analysis/output/sandbox_output/test_mb.root'
fout = ROOT.TFile( fout_id, "RECREATE" )

#Define histograms

#Wafers in motherboard
histList_motherboardMap = []
for motherboard_idx in range(1,N_motherboards+1):
  histList_motherboardMap.append( ROOT.TH2F("h_mb%g_map"%motherboard_idx, "Wafers in motherboard %g, layer = %g"%(motherboard_idx,hgcLayer), 50, 0, 25, 27, -1, 10.475  ) )

#Correlation motherboard maps: use dictionary
histList_motherboardCorrelationMap = {}
for mb_idx, neighbourMotherboards in motherboard_correlation_map.iteritems():
  #Loop over neighbouring motherboards
  for neighbourMotherboard in neighbourMotherboards:
    histList_motherboardCorrelationMap[ "%g_%g_corrMap"%(mb_idx,neighbourMotherboard) ] = ROOT.TH2F("h_mb%g-mb%g_corrMap"%(mb_idx,neighbourMotherboard), "Wafer in motherboard %g (yellow) and motherboard %g (green), layer = %g"%(mb_idx,neighbourMotherboard,hgcLayer), 50, 0, 25, 27, -1, 10.475  )

#Number of hits per motherboard: integrating cassettes
histList_motherboard = []
for motherboard_idx in range(1,N_motherboards+1):
  histList_motherboard.append( ROOT.TH1F("h_mb%g"%motherboard_idx,"Number of hits in motherboard = %g, Layer = %g"%(motherboard_idx,hgcLayer),300,0,600) )

#Correlation motherboard plots: only plot for physically connected motherboards
# 2D histogram with nhits of x_mb - vs - nhits of y_mb
histList_motherboardCorrelation = {}
for mb_idx, neighbourMotherboards in motherboard_correlation_map.iteritems():
  #Loop over neighbouring motherboards
  for neighbourMotherboard in neighbourMotherboards:
    histList_motherboardCorrelation[ "%g_%g_corrPlot"%(mb_idx,neighbourMotherboard) ] = ROOT.TH2F("h_mb%g-mb%g_corr"%(mb_idx,neighbourMotherboard), "Number of hits in motherboard %g - vs - motherboard %g (green), layer = %g"%(mb_idx,neighbourMotherboard,hgcLayer), 600, 0, 600, 600, 0, 600  )

################################################################################################
#Fill histogram giving wafers in layer/motherboard
for wafer_key in module_map:
  wafer = wafer_key.split(",")
  waferuv = [int( wafer[0][1:] ), int( wafer[1][:-1] )]
  waferxy = [-2*waferuv[0]+waferuv[1],((3**0.5)/2)*waferuv[1]]
  for hist in histList_motherboardMap: hist.Fill( waferxy[0], waferxy[1] )
  #extract motherboard
  module_key = module_map[ wafer_key ]
  motherboard_key = motherboard_map[ module_key ]
  histList_motherboardMap[ motherboard_key-1 ].Fill( waferxy[0], waferxy[1] )

#Fill correlation map histograms: x axis mb in (yellow) and y axis mb in (green)
for wafer_key in module_map:
  wafer = wafer_key.split(",")
  waferuv = [int( wafer[0][1:] ), int( wafer[1][:-1] )]
  waferxy = [-2*waferuv[0]+waferuv[1],((3**0.5)/2)*waferuv[1]]
  for key, hist in histList_motherboardCorrelationMap.iteritems(): hist.Fill( waferxy[0], waferxy[1] )
#Extract the modules in the connected motherboards
for key, hist in histList_motherboardCorrelationMap.iteritems():
  x_mb = int( key.split("_")[0] )
  y_mb = int( key.split("_")[1] )
  x_modules = motherboard_imap[ x_mb ]
  y_modules = motherboard_imap[ y_mb ]
  #Loop over modules in connected motherboards and fill relevant histograms by different weight
  for x_module in x_modules:
    x_module_uv = [int( x_module.split(",")[0][1:] ),int( x_module.split(",")[1][:-1] )]
    x_module_xy = [-2*x_module_uv[0]+x_module_uv[1],((3**0.5)/2)*x_module_uv[1]]
    hist.Fill( x_module_xy[0], x_module_xy[1], 3 )
  for y_module in y_modules:
    y_module_uv = [int( y_module.split(",")[0][1:] ),int( y_module.split(",")[1][:-1] )]
    y_module_xy = [-2*y_module_uv[0]+y_module_uv[1],((3**0.5)/2)*y_module_uv[1]]
    hist.Fill( y_module_xy[0], y_module_xy[1], 1 )

################################################################################################
#Loop over events in NTUP
eventCounter = 0

for event in tree:

  if eventCounter == maxEvents: break

  if( maxEvents < tree.GetEntries() )&( maxEvents > 0 ): print "Processing event: %g/%g"%(eventCounter,maxEvents-1)
  else: print "Processing event: %g/%g"%(eventCounter,tree.GetEntries()-1)

  #store number of hits per motherboard 
  cass0_posz_nhits_motherboard = [0]*N_motherboards
  cass1_posz_nhits_motherboard = [0]*N_motherboards
  cass2_posz_nhits_motherboard = [0]*N_motherboards
  cass3_posz_nhits_motherboard = [0]*N_motherboards
  cass4_posz_nhits_motherboard = [0]*N_motherboards
  cass5_posz_nhits_motherboard = [0]*N_motherboards
  cass0_negz_nhits_motherboard = [0]*N_motherboards
  cass1_negz_nhits_motherboard = [0]*N_motherboards
  cass2_negz_nhits_motherboard = [0]*N_motherboards
  cass3_negz_nhits_motherboard = [0]*N_motherboards
  cass4_negz_nhits_motherboard = [0]*N_motherboards
  cass5_negz_nhits_motherboard = [0]*N_motherboards
 
  nhits_motherboard = {"cass0_posz":cass0_posz_nhits_motherboard, "cass1_posz":cass1_posz_nhits_motherboard, "cass2_posz":cass2_posz_nhits_motherboard, "cass3_posz":cass3_posz_nhits_motherboard, "cass4_posz":cass4_posz_nhits_motherboard, "cass5_posz":cass5_posz_nhits_motherboard, "cass0_negz":cass0_negz_nhits_motherboard, "cass1_negz":cass1_negz_nhits_motherboard, "cass2_negz":cass2_negz_nhits_motherboard, "cass3_negz":cass3_negz_nhits_motherboard, "cass4_negz":cass4_negz_nhits_motherboard, "cass5_negz":cass5_negz_nhits_motherboard }

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
              #determine motherboardID of hit
              motherboard = hit.motherboardID()
              #add hit to motherboard counter: -1 as counter starts from 0
              nhits_motherboard[ 'cass%g_posz'%cassette ][motherboard-1] += 1
       
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
              #determine motherboardID of hit
              motherboard = hit.motherboardID()
              #add hit to motherboard counter: -1 as counter starts from 0
              nhits_motherboard[ 'cass%g_negz'%cassette ][motherboard-1] += 1


    #For hits in the scintillator panels
    #if( isScint( event, hit_idx ) ):
  
  #Fill Nhits in motherboards histogram
  for motherboard_idx in range(0,N_motherboards):
    for zside in ['posz','negz']:
      for cassette_idx in range(0,6):
        histList_motherboard[motherboard_idx].Fill( nhits_motherboard[ 'cass%g_%s'%(cassette_idx,zside) ][motherboard_idx] )

  #Fill correlation plots histograms:
  for x_mb_idx in range(0,N_motherboards):
    for y_mb_idx in range(0,N_motherboards):
      #If correlation plot in list to be filled
      if '%g_%g_corrPlot'%(x_mb_idx+1,y_mb_idx+1) in histList_motherboardCorrelation:
        for zside in ['posz','negz']:
          for cassette_idx in range(0,6):
            histList_motherboardCorrelation[ '%g_%g_corrPlot'%(x_mb_idx+1,y_mb_idx+1) ].Fill( nhits_motherboard[ 'cass%g_%s'%(cassette_idx,zside) ][x_mb_idx], nhits_motherboard[ 'cass%g_%s'%(cassette_idx,zside) ][y_mb_idx] )

  #Add to event counter
  eventCounter +=1

#End of events loop
  
################################################################################################
#Close root file to write to
fout.Write()
fout.Close()
