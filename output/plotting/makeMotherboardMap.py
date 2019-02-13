import ROOT
import sys

if len(sys.argv) != 3:
  print "Usage: makeCassettePlot.py <layer idx> <motherboard idx>"
  sys.exit(1)

layer_idx = int(sys.argv[1])
motherboard_idx = int(sys.argv[2])

#open root file to read from
f = ROOT.TFile.Open("HGCalChannel_SiOnly_layer%g.root"%layer_idx)

#Initiate canvas
canv = ROOT.TCanvas("c","c",10,32,700,502)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetPalette(51)
canv.SetFrameLineColor(0)

#Extract histogram
h = f.Get("h_mb%g"%motherboard_idx)

h.SetTitle("")
#h.GetYaxis().SetTitle("y of wafer centre")
h.GetYaxis().SetLabelSize(0)
h.GetYaxis().SetLabelOffset(999)
h.GetYaxis().SetTickSize(0)
h.GetYaxis().SetTitleSize(0.04)
h.GetYaxis().SetTitleOffset(1.1)
#h.GetXaxis().SetTitle("x of wafer centre")
h.GetXaxis().SetLabelSize(0)
h.GetXaxis().SetLabelOffset(999)
h.GetXaxis().SetTickSize(0)
h.GetXaxis().SetTitleSize(0)
h.GetXaxis().SetTitleOffset(1.4)

h.Draw("COL BOX ARROW A")
canv.SetBottomMargin(0.15)

lat = ROOT.TLatex()
lat.SetTextFont(42)
lat.SetLineWidth(2)
lat.SetTextAlign(11)
lat.SetNDC()
lat.SetTextSize(0.05)
lat.DrawLatex(0.1,0.92,"#bf{HGCal} #scale[0.75]{#it{Geometry v9}}")
lat.DrawLatex(0.5,0.92,"Layer = %g, Motherboard = %g"%(layer_idx,motherboard_idx))

#Draw u and v axes
#axis_u = ROOT.TGaxis( 23, -0.866, -3, -0.865, -12, 1, 13, "+L")
#axis_v = ROOT.TGaxis( -3, -0.866, 10, 10.392, -1, 12, 13, "+L")
#axis_u.Draw("Same") 
#axis_v.Draw("Same") 

#canv.Print("/afs/cern.ch/work/j/jolangfo/hgcal/test/CMSSW_10_4_0_pre1/src/Demo/HGCalAnalyzer/test/output/globalHist/CassettePlots/wafer_%s_layer%g.pdf"%(plotName,layer_idx))

raw_input("Press Enter to continue...")
