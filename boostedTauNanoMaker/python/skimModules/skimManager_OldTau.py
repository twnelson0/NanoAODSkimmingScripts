import ROOT
import json
import re
from tqdm import tqdm
from cutManager import cutManager
import math

class skimManager():
    def __init__(self):
        pass

    def deltaR(self, eta1, phi1, eta2, phi2):
        """Calculate delta R."""
        dEta = eta1 - eta2
        dPhi = abs(phi1 - phi2)
        if dPhi > math.pi:
            dPhi -= 2 * math.pi
        return math.sqrt(dEta**2 + dPhi**2)

    def skimAFile(self,
                  fileName,
                  branchCancelationFileName,
                  theCutFile,
                  outputFileName,
                  deltaR_min=0.1,
                  deltaR_max=0.8,
                  muonSelection=lambda pt, eta, id: pt > 50 and abs(eta) < 2.4 and id > 0.5,
                  tauSelection=lambda pt, eta: pt > 20 and abs(eta) < 2.3):

        try:
            #print("trying to open the file")
	    #hdfsFileName = fileName.replace('/hdfs','root://cmsxrootd.hep.wisc.edu//')
            theLoadFile = ROOT.TFile(fileName)
            theInputTree = theLoadFile.Events
            theRunTree = theLoadFile.Runs
        except: #we failed to open the file properly, so let's try it the other way
            try:
		#print ("Went to Ecept statement")
                theLoadFile = ROOT.TFile.Open(fileName)
                theInputTree = theLoadFile.Events
                theRunTree = theLoadFile.Runs
            except: #we have failed again to find the file. Let's try to open it this way
                hdfsFileName = ''
                if 'xrootd' in fileName: #we're already tried toopen xrootd style. We're done here
                    hdfsFileName = fileName.replace('hdfs/','')
                else:
                    hdfsFileName = fileName.replace('/hdfs','root://cmsxrootd.hep.wisc.edu//')
                    print(hdfsFileName)
                print(hdfsFileName)
                print("Last attempt to load the file at /hdfs/ with: "+hdfsFileName)
                try:
                    theLoadFile = ROOT.TFile.Open(hdfsFileName)
                    theInputTree = theLoadFile.Events
                    theRunTree = theLoadFile.Runs
                except:
                    print("Failed to load the files properly!")
                    print("Exiting with code -1")
                    exit(-1)

        print('Loaded the file, and retrieved the trees...')
        
        branchCancelations = None
        if branchCancelationFileName is not None:
            print('\n checking the branches\n') 
            branchCancelationFile = open(branchCancelationFileName)
            branchCancelationJSON = json.load(branchCancelationFile)
            branchCancelationFile.close()
            try:
                branchCancelations = [re.compile(branchCancelationJSON[x]) for x in branchCancelationJSON]
            except Exception as err:
                print('Failed to make proper RE\'s for branch cancelations')
                print(err)
                exit(-1)

        theCutManager = cutManager(theInputTree, theCutFile)
        
        nBranches = theInputTree.GetNbranches()
        listOfBranches = theInputTree.GetListOfBranches()
        #now we loop over branches, and the branch cancellation REs
        #if one of the RE's matches, disable the branch.
        if branchCancelations != None:
            for branchIndex in range(nBranches):
                for REIndex in range(len(branchCancelations)):
                    theRE = branchCancelations[REIndex]
                    theBranchName = listOfBranches[branchIndex].GetName()
                    if theRE.search(theBranchName):
                        theInputTree.GetBranch(theBranchName).SetStatus(0) # close out the branch and don't copy it
        #all branches should be canceled now
        #now let's set up a new file/tree
        theOutputFile = ROOT.TFile(outputFileName,'RECREATE') #this has to happen last to keep things associated with it


        theCutFlow = theCutManager.createCutFlowHistogram()
        theCutFlow.Write('cutflow', ROOT.TFile.kOverwrite)

        finalCut = theCutManager.createAllCuts()
        print('Performing final tree copy...')

        # Create new tree to hold filtered events
        theOutputTree = theInputTree.CloneTree(0)

        for event in tqdm(theInputTree, total=theInputTree.GetEntries()):
            print('Running on events to apply dR cuts...')
            # Apply event-level cuts
#            if not eval(finalCut): #Apply the cuts from the cuts.json file
#                continue

            # Simplified Delta R filtering logic
            passesDeltaRCut = True
            muons = [
                (event.Muon_eta[i], event.Muon_phi[i], event.Muon_pt[i])
                for i in range(event.nMuon)
                if muonSelection(event.Muon_pt[i], event.Muon_eta[i],event.Muon_looseId[i])
            ]
            # Select taus
            taus = [
                (event.boostedTau_eta[i], event.boostedTau_phi[i], event.boostedTau_pt[i])
                for i in range(event.nboostedTau)
                if tauSelection(event.boostedTau_pt[i], event.boostedTau_eta[i])
            ]
            # Apply delta R cut
            passesDeltaRCut = False
            for muon_eta, muon_phi, _ in muons:
                for tau_eta, tau_phi, _ in taus:
                    deltaR = self.deltaR(muon_eta, muon_phi, tau_eta, tau_phi)
                    if deltaR_min < deltaR < deltaR_max:
                        passesDeltaRCut = True
                        break
                if passesDeltaRCut:
                    break
            if not passesDeltaRCut:
                continue
            theOutputTree.Fill()

        theOutputFile.cd()
        print('Writing all output...')
        theOutputTree.Write('Events', ROOT.TFile.kOverwrite)
        theRunTree.CopyTree('').Write('Runs', ROOT.TFile.kOverwrite)
        theOutputFile.Write()
        theOutputFile.Close()
        theLoadFile.Close()

