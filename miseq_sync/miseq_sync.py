import pandas as pd
from redmine import Redmine
import sh
from path import Path
import argparse
from datetime import date
import sys
#NOTE: ngsdir is really miseqdir
'''
Given: Run name, Issue ID
  State of: sync PBS job was just run

1. Compare samplesheet with issue samplelist
   * Error if samplenames are missing
   * reassign to author and set to error if different, reporting samplesheet
   * else continue
2. Relate run to sample issues
   * Search for existing samples and relate them
   * Create and relate new issues for samples without search matches
3. Rename  ReadData
   * Make a mapping M of SampleName <=> Issue ID
   * Use M to rename ReadData files with ID and date
4. SymLink ReadData reads into ReadsBySample
   * Create folders for all new issues
      * error if those folders exist
   * Symlink (relative) ReadData reads into their ID folders


1. fetch samplelist
config.ngsdir
config.url
config.apikey
'''
## Redmine Utilities ##
def set_status(runIssue, statusname): # -> None
  '''
  Set the status_id of the job
  Finds the correct status_id based on the status name given
  and then uses that to set the status

  New , Sequencing , Data Transfer , Completed , Error
  :param str statusname: Status name to set
  '''
  valid_statuses = (
      'New',
      'Sequencing',
      'Data Transfer',
      'Completed',
      'Error'
  )
  # First locate the status resource by name
  all_status = runIssue.manager.redmine.issue_status.all()
  _status = None
  for status in all_status:
      if status.name == statusname:
          _status = status
          break
  # Ensure it is a valid status
  if _status is None or statusname not in valid_statuses:
      raise InvalidStatus("{0} is an invalid status".format(statusname))
  # set the status_id of this resource
  runIssue.status_id = _status.id
  runIssue.__dict__['_attributes']['status']['id'] = _status['id']
  runIssue.__dict__['_attributes']['status']['name'] = _status['name']

def cf(issue, fname): # -> str
  return [d['value'] for d in issue.custom_fields.resources if d['name'] == fname][0]

def new_sample(R, sampleName):
    samples_id = R.project.get('samples').id
    return R.issue.create(project_id=samples_id, subject=sampleName)

def relate_samples(R, ss, run): # -> ([Sample, Sample])
  old_matches, new_matches = [], []
  for sampleName in ss.Sample_Name:
    existing = list(R.issue.filter(subject=sampleName))
    if len(existing) > 1:
      raise ValueError("Multiple issues with name {}".format(sampleName))
    old_matches += existing
    if not existing:
      new_matches += [ new_sample(sampleName) ]
  for sample in old_matches + new_matches:
    R.issue_relation.create(relation_type='blocks', issue_id=run.id, to_id=sample.id)
  return old_matches, new_matches

def verify_sample_list(ss, run): # -> Bool
  sampleList = cf(run, 'SampleList').splitlines()
  # order of sl and ss expected to be the same
  if sampleList != ss.Sample_Name.values.tolist():
    sampleListError =  "Sample List did not match Sample Sheet. Please adjust SampleList to match: \n {0}"
    run.notes = sampleListError.format("\n".join(ss.Sample_Name))
    run.assigned_to_id = run.author.id
    set_status(run, "Error")
    run.save()
  return sampleList == ss.Sample_Name.values.tolist()

### Filesystem Functions
def sample_sheet_to_df(filename): # -> pd.DataFrame
  filehandle = open(filename)
  s = filehandle.read()
  meta_info_striped = io.BytesIO(s[s.find('[Data]') + len('[Data]'):].strip())
  filehandle.close()
  return pd.read_csv(meta_info_striped)

def get_readdata_fastqs(readdata, runname, prefix): # -> [Path]
  matches = readdata.glob('{}*.fastq'.format(prefix))
  return map(Path, matches)

def rename_issue_date(path, sample): # -> str
    new_basename = Path(path.basename().replace(sample.subject, str(sample.id)))
    today = date.today().isoformat().replace('-','_')
    return "{}_{}.fastq".format(new_basename.stripext(), today)

def rename_readdata_fastqs(ngsdir, runname, sample): # -> None
  readdata = ngsdir / 'ReadData' / runname
  matches = get_readdata_fastqs(readdata, runname, sample.subject)
  for match in matches:
    #match.rename(readdata / new_basename)
    new_basename = rename_issue_date(match, sample)
    sh.mv(match, readdata / new_basename)

### Main, Error-handling
def execute(R, ngsdir, runID): # -> None
  run = R.project.get('vdbsequencing').issues.get(runID)
  runname = cf(run, 'Run Name')
  #TODO: assert run name is non-empty
  ss_filename = ngsdir / 'RawData' / runname / 'SampleSheet.csv'
  ss = sample_sheet_to_df(ss_filename)
#  if ss.Sample_Name.empty:
#    raise ValueError("Sample Names missing from file {}".format(ss_filename))
  if ss.isnull().values.any() or ss.Sample_Name.empty:
    raise ValueError("Sample Names or Sample IDs missing from file {}".format(ss_filename))
  if not verify_sample_list(ss, run):
    raise ValueError("Sample List did not match Sample Sheet.")
  old_matches, new_matches = relate_samples(R, ss, run)
  for sample in old_matches + new_matches:
    rename_readdata_fastqs(ngsdir, runname, sample)
  # Link everything to ReadsBySample
  def sample_dir(sample): return ngsdir / 'ReadsBySample' / str(sample.id)
  for newSample in new_matches:
    sh.mkdir(sample_dir(newSample))
  for sample in old_matches + new_matches:
    for oldfile in get_readdata_fastqs(ngsdir, runname, sample.id):
      newfile = sample_dir(sample) / oldfile.basename()
      sh.ln(oldfile, newfile, s=True)
  set_status(run, 'Completed')
  run.save()

def parse_args(sysargs):
    parser = argparse.ArgumentParser()
    parser.add_argument('--key', required=True)
    parser.add_argument('--url', required=True)
    parser.add_argument('--ngsdir', required=True, type=Path)
    parser.add_argument('--runissue', required=True, type=int)
    return parser.parse_args(sysargs)

def main():
    args = parse_args(sys.argv[1:])
    R = Redmine(url=args.url, key=args.key)
    execute(R, args.ngsdir, args.runissue)
    return 0




