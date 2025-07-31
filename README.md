## Running Instructions
Command must be run within `boostedTauNanoMaker/scripts/`
```bash
python skimNtuples.py --skimFileConfiguration 'location of json files containing nanoAODs to be skimmed' --skimCutConfiguration ../../metaData/skimmingCuttingConfigurations/2017_18_looserGeneralSkimCuttingConfiguration.json --skimBranchCancelations ../../metaData/branchCancelationConfigurations/Null_Cancelation.json --destination 'Location of skimmed nanoAODs' --skimSuffix Newskim_Debugging --prepareCondorSubmission
```
