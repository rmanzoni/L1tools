#!/usr/bin/env python

"""
Example L1TNtuple analysis program
"""

import ROOT
from copy import deepcopy as dc

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(1)
ROOT.TH1.SetDefaultSumw2(True)
ROOT.gStyle.SetOptStat(0)

class L1Tau(object):
    def __init__(self, et = -99., eta = -99., phi = -99. , iso = -1, bx = -99):
        self.et  = et 
        self.eta = eta
        self.phi = phi
        self.iso = iso
        self.bx  = bx
    
    def __str__(self):
        return 'Et = %.2f \t eta %.2f \t phi %.2f \t iso %d \t bx %d' %(self.et , self.eta, self.phi, self.iso, self.bx)

def eventLoop(files, total_rate = 1., nevents = -1, verbose = False):
    '''
    Plots di-iso tau rates.
    total_rate should be put equal to the total rate of the run on which this is run
    '''

    outfile = ROOT.TFile.Open('rate_histograms.root', 'recreate')

    differential_rate = ROOT.TH1F('ditau_differential_rate', 'ditau_differential_rate', 80, 0., 80.)
    cumulative_rate   = dc(differential_rate)
    cumulative_rate.SetTitle('ditau_cumulative_rate')
    cumulative_rate.SetName ('ditau_cumulative_rate')

    print 'start loading %d files' %len(files)
    
    treeEvent = ROOT.TChain("l1EventTree/L1EventTree")
    treeL1up  = ROOT.TChain("l1UpgradeEmuTree/L1UpgradeTree")

    for file in files:
        treeEvent.Add(file)
        treeL1up .Add(file)

    print 'loaded %d files containing %d events' %(len(files), treeEvent.GetEntries())

    treeEvent.AddFriend(treeL1up)

    for jentry, event in enumerate(treeEvent):
        if jentry%10000 == 0:
            print '=============================> event %d / %d' %(jentry, treeEvent.GetEntries())
        if nevents > 0 and jentry >= nevents:
            break
        
        ev  = treeEvent.Event
        sim = treeL1up.L1Upgrade
        
        if verbose: print '\nevent: %d, ntaus: %d' %(ev.event, sim.nTaus)
        
        taus = []
        
        for i in range(sim.nTaus):
            taus.append(L1Tau(sim.tauEt[i], sim.tauEta[i], sim.tauPhi[i], sim.tauIso[i], sim.tauBx[i]))
        
        taus.sort(key=lambda x: (x.iso, x.et), reverse=True)
                
        for i, tau in enumerate(taus):
            if verbose: print '\ttau %d \t' %i, tau
        
        
        isotaus = [tau for tau in taus if tau.iso == 1 and abs(tau.eta) < 2.17 and tau.bx == 0]
        
        if len(isotaus) < 2:
            continue
                
        differential_rate.Fill(isotaus[1].et)    
    
    outfile.cd()
    differential_rate.Write()     
    differential_rate.Draw('HIST')
    ROOT.gPad.SaveAs('differential_rate.pdf')

    allevents = float(treeEvent.GetEntries() if nevents<0 else nevents)

    bins = []

    for bin in range(differential_rate.GetNbinsX()):
        bins.append( float(differential_rate.GetBinContent(bin+1)) )

    rates = []
    
    for i, bin in enumerate(bins):
        rates.append(total_rate * sum(bins[i:]) / allevents)
    
    for bin in range(cumulative_rate.GetNbinsX()):
        cumulative_rate.SetBinContent(bin+1, rates[bin])

    ROOT.gPad.SetLogy()
    
    outfile.cd()
    cumulative_rate.Write()     
    cumulative_rate.Draw('HIST')
    ROOT.gPad.SaveAs('rate.pdf')
    


if __name__ == "__main__":
    eventLoop(['root://xrootd.unl.edu//store/group/dpg_trigger/comm_trigger/L1Trigger/L1Menu2016/Stage2/l1-tsg-v4/ZeroBias2/crab_l1-tsg-v4__259721_ZeroBias2/160315_144909/0000/L1Ntuple_%d.root' % i for i in range(1,35)])
