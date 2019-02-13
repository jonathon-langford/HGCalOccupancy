import ROOT
import sys
import os
from optparse import OptionParser

shiftLayer = True

ROOT.gROOT.SetBatch(ROOT.kTRUE)

def get_options():
  parser = OptionParser()
  parser = OptionParser( usage="usage: python makeMotherboardPlot.py <layer [1,36]> <motherboard [1,# of motherboards in layer]>" )
  parser.add_option("-l", "--layer", dest="layer_idx", default=1, help="HGCal Layer")
  return parser.parse_args()

(opt,args) = get_options()
layer_idx = int( opt.layer_idx )

maxMotherboard = {1:15,2:13,3:15,4:12,5:15,6:13,7:16,8:13,9:16,10:13,11:15,12:15,13:14,14:14,15:15,16:14,17:15,18:13,19:17,20:15,21:17,22:15,23:18,24:15,25:18,26:14,27:18,28:14,29:20,30:19,31:19,32:20,33:17,34:21,35:21,36:23}
if layer_idx not in maxMotherboard:
  print "Layer does not exist. Please enter number: [1,36]. Leaving"
  sys.exit(1)

#open root file to read from
f = ROOT.TFile.Open(os.environ['CMSSW_BASE']+'/src/analysis/output/hist_SiOnly/HGCalOccupancy_SiOnly_layer%g.root'%layer_idx)

#Blacklist layers as problem
if layer_idx == 34: sys.exit(1)

#Loop over motherboards
for mb_idx in range(1,maxMotherboard[layer_idx]+1):

  #If only want to output one plot
  #if mb_idx != 1: continue

  #Extract histograms
  h_mb = f.Get("h_mb%g"%mb_idx)
  h_map = f.Get("h_mb%g_map"%mb_idx)

  #Normalise histogram
  h_mb.Scale(1./h_mb.GetEntries())

  #Determine the mean hist and rms, and rescale histogram accordingly
  mean = h_mb.GetMean()
  rms = h_mb.GetRMS()
  if( rms < 2. ): h_mb.GetXaxis().SetRangeUser( mean-3*rms, 20 )
  else: h_mb.GetXaxis().SetRangeUser( mean-3*rms, mean+6*rms )
  h_mb.SetMinimum(0.)
  
  #Initiate canvas
  canv = ROOT.TCanvas("c","c",10,32,700,502)
  ROOT.gStyle.SetOptStat(0)
  ROOT.gStyle.SetPalette(51)
  canv.SetBottomMargin(0.15)
  canv.SetLeftMargin(0.12)
  
  #Plotting options
  h_mb.SetTitle("")
  h_mb.GetYaxis().SetTitle("Fractional Entries")
  h_mb.GetYaxis().SetLabelSize(0.04)
  h_mb.GetYaxis().SetTitleSize(0.04)
  h_mb.GetYaxis().SetTitleOffset(1.3)
  h_mb.GetXaxis().SetTitle("Number of reconstructed hits")
  h_mb.GetXaxis().SetLabelSize(0.04)
  h_mb.GetXaxis().SetTitleSize(0.04)
  h_mb.GetXaxis().SetTitleOffset(1.4)

  h_mb.Draw()

  #Configure motherboard map
  h_map.SetTitle("")
  h_map.GetYaxis().SetLabelSize(0)
  h_map.GetYaxis().SetLabelOffset(999)
  h_map.GetYaxis().SetTickSize(0)
  h_map.GetYaxis().SetTitleSize(0.04)
  h_map.GetYaxis().SetTitleOffset(1.3)
  h_map.GetXaxis().SetLabelSize(0)
  h_map.GetXaxis().SetLabelOffset(999)
  h_map.GetXaxis().SetTickSize(0)
  h_map.GetXaxis().SetTitleSize(0)
  h_map.GetXaxis().SetTitleOffset(1.4)
  #Draw in inner pad
  inner_pad = ROOT.TPad("subpad","",0.5,0.45,0.90,0.89)
  inner_pad.SetFrameLineColor(0)
  inner_pad.Draw()
  inner_pad.cd()
  h_map.Draw("COL BOX ARROW A")

  #cd back to full canvas
  canv.cd()
  lat = ROOT.TLatex()
  lat.SetTextFont(42)
  lat.SetLineWidth(2)
  lat.SetTextAlign(11)
  lat.SetNDC()
  lat.SetTextSize(0.05)
  lat.DrawLatex(0.1,0.92,"#bf{HGCal} #scale[0.75]{#it{Geometry v9}}")
  if( shiftLayer ): lat.DrawLatex(0.5,0.92,"Layer = %g, Motherboard = %g"%(layer_idx-1,mb_idx))
  else: lat.DrawLatex(0.5,0.92,"Layer = %g, Motherboard = %g"%(layer_idx-1,mb_idx))
  lat.DrawLatex(0.65,0.4,"#scale[0.75]{<hits> = %4.2f}"%mean)
  lat.DrawLatex(0.65,0.3,"#scale[0.75]{RMS = %4.2f}"%rms)

  #Save canvas and close
  canv.Print("/eos/user/j/jlangfor/www/CMS/HGCal/Occupancy_Studies/motherboard_hit_distributions/lay%g/layer%g_mb%g.pdf"%(layer_idx-1,layer_idx-1,mb_idx))
  canv.Print("/eos/user/j/jlangfor/www/CMS/HGCal/Occupancy_Studies/motherboard_hit_distributions/lay%g/layer%g_mb%g.png"%(layer_idx-1,layer_idx-1,mb_idx))
 
  canv.Close()
