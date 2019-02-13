import ROOT
import sys
import os

if len(sys.argv) != 3:
  print "Usage: makeModulePlot.py <layer idx> <module idx>"
  sys.exit(1)

layer_idx = int(sys.argv[1])
m_idx = int(sys.argv[2])
plotName = 'module'

#open root file to read from
f = ROOT.TFile.Open(os.environ['CMSSW_BASE']+'/src/analysis/output/hist_SiOnly/HGCalChannel_SiOnly_layer%g.root'%layer_idx)

#Initiate canvas
canv = ROOT.TCanvas("c","c",900,700)

h = f.Get("h_%s%g"%(plotName,m_idx))

#h.SetTitle("")
h.GetYaxis().SetTitle("Entries")
h.GetYaxis().SetLabelSize(0.04)
h.GetYaxis().SetTitleSize(0.04)
h.GetYaxis().SetTitleOffset(1.1)
h.GetXaxis().SetTitle("Number of hits")
h.GetXaxis().SetLabelSize(0.04)
h.GetXaxis().SetTitleSize(0.04)
h.GetXaxis().SetTitleOffset(1.4)

h.Draw("")
canv.SetBottomMargin(0.15)

lat = ROOT.TLatex()
lat.SetTextFont(42)
lat.SetLineWidth(2)
lat.SetTextAlign(11)
lat.SetNDC()
lat.SetTextSize(0.05)
#lat.DrawLatex(0.1,0.92,"#bf{HGCal} #scale[0.75]{#it{Simulation}}")
lat.DrawLatex(0.5,0.6,"ttbar 200PU")
lat.DrawLatex(0.5,0.5,"Geometry: v9 (D28)")

#canv.Print("/afs/cern.ch/work/j/jolangfo/hgcal/test/CMSSW_10_4_0_pre1/src/Demo/HGCalAnalyzer/test/output/hist/%s/%s%g_layer%g.pdf"%(plotName,plotName,m_idx,layer_idx))

raw_input("Press Enter to continue...")
