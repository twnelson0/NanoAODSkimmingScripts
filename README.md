## Installation
Code has only been tested and is only known to work with `CMSSW_10_6_27`

Check out CMSSW release
```
cmsrel CMSSW_10_6_27
cd CMSSW_10_6_27/src
cmsenv
```
Clone the repository into `CMSSW_10_6_27/src`

Then run the scram build command in `CMSSW_10_6_27/src`
```
scram build -j 8
```


## Running Instructions
The skimming code is run from within the directory `boostedTauNanoMaker/scripts/`

The script that performs the skimming is a script called `skimManager.py` it is contained in the directory `NanoAODSkimmingScripts/boostedTauNanoMaker/python/skimModules`

To skim on a given set of files 
```bash
python skimNtuples.py --skimFileConfiguration 'location of json files containing nanoAODs to be skimmed' --skimCutConfiguration ../../metaData/skimmingCuttingConfigurations/2017_18_looserGeneralSkimCuttingConfiguration.json --skimBranchCancelations ../../metaData/branchCancelationConfigurations/Null_Cancelation.json --destination 'Desired_Location_Of_Output_Skimmed_Files' --skimSuffix "Suffix for skimmed files" --prepareCondorSubmission
```

**Overview of the Arguments for `skimNtuples.py`**
`--skimFileConfiguration` must be a `.json` file containing a collection of samples and files of the following form:
```json
{
    "Sample_Name": "/location/of/nanoAODs/*.root"
}
```
For all tests I have performed I have used JSON files stored in `NanoAODSkimmingScripts/metaData/skimmingFiles/`

`--skimCutConfiguration`  JSON file describing the cuts to be implemented (I have always passed in the json file `NanoAODSkimmingScripts/metaData/skimmingCuttingConfigurations/2017_18_looserGeneralSkimCuttingConfiguration.json` for this argument)

`--skimBranchCancelations` JSON file denoting branches that do not need to be ported into the skimmed nanoAOD (I have always used the configuration denoted by the JSON file `NanoAODSkimmingScripts/metaData/branchCancelationConfigurations/Null_Cancelation.json`)

`--destination` Denotes in what directory the skimmed files should be stored in

`--skimSuffix` Suffix of directory containing skimmed NanoAODs
