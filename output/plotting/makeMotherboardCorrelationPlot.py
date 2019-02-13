import ROOT
import sys
import os
from optparse import OptionParser

shiftLayer = True
auto_rebin = True
binScaler_x_global = 5
binScaler_y_global = 5
# if auto-rebinning: set number of bins require on axis
nBins_x = 30
nBins_y = 30

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gErrorIgnoreLevel = ROOT.kWarning

def get_options():
  parser = OptionParser()
  parser = OptionParser( usage="usage: python makeMotherboardCorrelationPlot.py <layer [1,36]>" )
  parser.add_option("-l", "--layer", dest="layer_idx", default=1, help="HGCal Layer")
  return parser.parse_args()

(opt,args) = get_options()
layer_idx = int( opt.layer_idx )

#Define the total number of motherboards in each layer
maxMotherboard = {1:15,2:13,3:15,4:12,5:15,6:13,7:16,8:13,9:16,10:13,11:15,12:15,13:14,14:14,15:15,16:14,17:15,18:13,19:17,20:15,21:17,22:15,23:18,24:15,25:18,26:14,27:18,28:14,29:20,30:19,31:19,32:20,33:17,34:21,35:21,36:23}

if layer_idx not in maxMotherboard:
  print "Layer does not exist. Please enter number: [1,36]. Leaving"
  sys.exit(1)

#open root file to read from
f = ROOT.TFile.Open(os.environ['CMSSW_BASE']+'/src/analysis/output/hist_SiOnly/HGCalOccupancy_SiOnly_layer%g.root'%layer_idx)
#f = ROOT.TFile.Open(os.environ['CMSSW_BASE']+'/src/analysis/output/hist_SiOnly/lay1/HGCalOccupancy_SiOnly_layer%g_1_test.root'%layer_idx)

#Loop over all possible motherboard combinations
for x_mb_idx in range(1,maxMotherboard[layer_idx]+1):
  for y_mb_idx in range(1,maxMotherboard[layer_idx]+1):

    #if(x_mb_idx!=1)|(y_mb_idx!=2): continue

    #If correlation plot exists
    if f.Get("h_mb%g-mb%g_corr"%(x_mb_idx,y_mb_idx)): 
      #Extract correlation plot and map
      h_corr_initial = f.Get("h_mb%g-mb%g_corr"%(x_mb_idx,y_mb_idx))
      h_corrMap = f.Get("h_mb%g-mb%g_corrMap"%(x_mb_idx,y_mb_idx))

      #Correlation plot
      mean_x = h_corr_initial.GetMean(1)
      mean_y = h_corr_initial.GetMean(2)
      rms_x = h_corr_initial.GetRMS(1)
      rms_y = h_corr_initial.GetRMS(2)
      if auto_rebin: #Take initial histogram and rebin/set axis range according to distribution
        #Rebin histogram: extract new range (+-3sigma)
        range_x = 8*rms_x
        range_y = 8*rms_y
        #Bin scalers: how many bins to group
        binScaler_x = int(range_x/nBins_x)
        binScaler_y = int(range_y/nBins_y)
        
        #Check for errors
        if( binScaler_x < 1 )|( binScaler_y < 1 ): h_corr = h_corr_initial.Rebin2D(binScaler_x_global,binScaler_y_global)
        else: h_corr = h_corr_initial.Rebin2D(binScaler_x,binScaler_y)
      else: h_corr = h_corr_initial.Rebin2D(binScaler_x_global,binScaler_y_global)
      #Normalise new histogram
      h_corr.Scale(100./h_corr.GetEntries())
      #Set maxima and minima of new histogram
      h_corr.GetXaxis().SetRangeUser( mean_x-4*rms_x, mean_x+4*rms_x )
      h_corr.GetYaxis().SetRangeUser( mean_y-4*rms_y, mean_y+4*rms_y )

      #Initiate canvas
      canv = ROOT.TCanvas("c","c",10,32,700,502)
      ROOT.gStyle.SetOptStat(0)
      ROOT.gStyle.SetPalette(ROOT.kBird)
      canv.SetRightMargin(0.2)

      #histogram plotting options
      h_corr.SetTitle("")
      h_corr.GetXaxis().SetTitle("Number of reconstructed hits in mb %g"%x_mb_idx)
      h_corr.GetXaxis().SetTitleSize(0.04)
      h_corr.GetXaxis().SetLabelSize(0.04)
      h_corr.GetXaxis().SetTitleOffset(1.)
      h_corr.GetYaxis().SetTitle("Number of reconstructed hits in mb %g"%y_mb_idx)
      h_corr.GetYaxis().SetTitleSize(0.04)
      h_corr.GetYaxis().SetLabelSize(0.04)
      h_corr.GetYaxis().SetTitleOffset(1.1)
      h_corr.GetZaxis().SetTitle("[%]")
      h_corr.GetZaxis().SetTitleOffset(1.1)
      h_corr.Draw("COLZ")

      lat = ROOT.TLatex()
      lat.SetTextFont(42)
      lat.SetLineWidth(2)
      lat.SetTextAlign(11)
      lat.SetNDC()
      lat.SetTextSize(0.05)
      lat.DrawLatex(0.1,0.92,"#bf{HGCal} #scale[0.75]{#it{Geometry v9}}")
      if( shiftLayer ): lat.DrawLatex(0.75,0.92,"Layer = %g"%(layer_idx-1))
      else: lat.DrawLatex(0.7,0.92,"Layer = %g"%layer_idx)

      #Print canvas
      canv.Print("/eos/user/j/jlangfor/www/CMS/HGCal/Occupancy_Studies/motherboard_correlation_plots/lay%g/layer%g_mb%g-mb%g.pdf"%(layer_idx-1,layer_idx-1,x_mb_idx,y_mb_idx))
      canv.Print("/eos/user/j/jlangfor/www/CMS/HGCal/Occupancy_Studies/motherboard_correlation_plots/lay%g/layer%g_mb%g-mb%g.png"%(layer_idx-1,layer_idx-1,x_mb_idx,y_mb_idx))
      canv.Close()

      #Plotting the motherboard Map
      canv = ROOT.TCanvas("c","c",10,32,700,502)
      ROOT.gStyle.SetOptStat(0)
      ROOT.gStyle.SetPalette(ROOT.kBird)
      #Map
      h_corrMap.SetTitle("")
      h_corrMap.GetXaxis().SetLabelSize(0)
      h_corrMap.GetXaxis().SetLabelOffset(999)
      h_corrMap.GetXaxis().SetTickSize(0)
      h_corrMap.GetXaxis().SetTitleSize(0)
      h_corrMap.GetXaxis().SetTitleOffset(1.)
      h_corrMap.GetYaxis().SetLabelSize(0)
      h_corrMap.GetYaxis().SetLabelOffset(999)
      h_corrMap.GetYaxis().SetTickSize(0)
      h_corrMap.GetYaxis().SetTitleSize(0.04)
      h_corrMap.GetYaxis().SetTitleOffset(1.1)
      h_corrMap.Draw("COL BOX ARROW SAME")      

      lat = ROOT.TLatex()
      lat.SetTextFont(42)
      lat.SetLineWidth(2)
      lat.SetTextAlign(11)
      lat.SetNDC()
      lat.SetTextSize(0.05)
      lat.DrawLatex(0.1,0.92,"#bf{HGCal} #scale[0.75]{#it{Geometry v9}}")
      if( shiftLayer ): lat.DrawLatex(0.75,0.92,"Layer = %g"%(layer_idx-1))
      else: lat.DrawLatex(0.7,0.92,"Layer = %g"%layer_idx)
      lat.DrawLatex(0.14,0.8,"#scale[0.75]{#bullet Yellow = Motherboard %g}"%x_mb_idx)
      lat.DrawLatex(0.14,0.75,"#scale[0.75]{#bullet Green  = Motherboard %g}"%y_mb_idx)

      #Print canvas
      canv.Print("/eos/user/j/jlangfor/www/CMS/HGCal/Occupancy_Studies/motherboard_correlation_plots/lay%g/layer%g_mb%g-mb%g_MAP.pdf"%(layer_idx-1,layer_idx-1,x_mb_idx,y_mb_idx))
      canv.Print("/eos/user/j/jlangfor/www/CMS/HGCal/Occupancy_Studies/motherboard_correlation_plots/lay%g/layer%g_mb%g-mb%g_MAP.png"%(layer_idx-1,layer_idx-1,x_mb_idx,y_mb_idx))
      canv.Close()

