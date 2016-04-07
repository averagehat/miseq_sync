###Plan

:: RunIssue -> (SamleList, RunName)
* Grab the sample list
* Also fetch the RunName
* Validate the sample names: Should not have `/`,etc. (filepath restrictions). If fail, ERROR with suggested new sample list.
* If the sample list names do not match the file names, ERROR.

:: RunIssue -> SampleList -> (Map SampleName IssueId)
* Within the context of some run issue
* Search the Samples project for issues with the subject name equal to the sample name (from the sample list). (NOTE: how to do this search?)
* If there's a match:
   * link the sample issue to the run
* If there is no match:
   * Create a new issue for the sample
   * link that sample issue to the run
* return a map of issue id to sample name

:: (Map SampleName IssueId, RunName) -> NGSDataPath -> ()
1. Copy TMPDIR/RunName to RawData, renaming via SampleName->IssueId
2. create a RunName directory in ReadData
   * extract the gz files into this directory
3. create a directory in ReadsBySample for each sample
   *  symlink each readpair into its directory

:: RunIssue -> ()
1. Update the run issue to completed
2. Maybe log info there like where the files are and stuff.

(what do with undetermined data)?
(run miseqreport at some point)

#Algebra

##Data:

TODO

##Operations: 

###Redmine
* create an issue (need to use result)
* search for sample name (need to use results)
* link two issues
* read a sample list
* Construct a SampleIssue

###FileSystem

* SymLink
* Copy
* ReadFile (SampleSheet) (?), no, just read the sample list
# * Rename(?)


###More Stuff

Tech pastes sample list into issue
tech pastes sample list into miseq machine
tech runs machine;
tech transfers data to TMPDIR

We run `sync_latest_miseq.pbs`: ngs_mapper.miseq_sync (via qsub)
the runpath is determined by the directory containing the most recently touched samlpesheet.
we run miseqreport.py on the runpath, outputs tothe syncpath
syncpath=/media/VD_Research/NGSData/RawData/MiSeq/${runname}

(miseq_sync.py copies a bunch of stuff and we get the samplenames as directories in ReadsBySample)

remove watchers etc, use apikey, run `syncsample.py`, select correct issue
add watchers & author back

extract sample name/id from samplesheet;
look up the issue IDs by sample name; (`get_issue_id.py`)
run `rename_sample` with each samplename and issue id.



miseq_sync.py
--------------
1.  Copies .gz files to RawData/$runpath/Data/Intensities/BaseCalls
2.  extracts .fastq files to ReadData/$runpath, but with run date in the name (before .fastq)
3.  creates ReadsBySample/<samplename> for each samplename, and links to the fastq files in REadData (name stays the same)
(the <samplename> is the field before the first unerscore)

syncsample.py
-------------
in redsample/bin
    sr = SequenceRequest( args.url, args.key )
    sr.DRY = args.dry # dry is dry-run
    sr.sync_requests()

get_issue_id.py
---------------
in redsample/bin

rename_sample.py
----------------
rename_sample.py:main


#TODO
* Drop any existing support for non-miseq data
* Ensure correct permissions after syncing
* ensure have permissions before syncing
* It's no longer necessary to `rsync`, seeing as the data is already local in TMPDIR
* samplesheet parsing is repeated code
* should just fetch the IDs when running syncsample.py instead of using get_issue_id.py
* `rename_sample.py` contains a bunch of non-MiSeq support
why copy sample dirs into ReadsBySample?
* do validation immediately on the sample names

15:02

    Sync issue to vdbpm creating issue id's for all samples
    Rename fastq.gz
    miseq_sync

