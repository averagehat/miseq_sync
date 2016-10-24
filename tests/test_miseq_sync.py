import mock
import itertools
# Config = NamedTuple('Config', ['key', 'url', 'ngsdir', 'runissue'])
import pytest
from pytest_mock import mocker
from hypothesis import given, assume, strategies as st
from collections import namedtuple
from miseq_sync import miseq_sync
from path import Path
samplesheet_text = '''
[Reads]
251
251
[Data]
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,GenomeFolder,Sample_Project,Description
020515DV2-S16803,,20151008_Dengue,A01,N701,TAAGGCGA,S513,TCGACTAG,PhiX\Illumina\RTA\Sequence\WholeGenomeFasta,,
020515DV2-IQT2913,020515DV2-IQT2913,20151008_Dengue,A02,N702,CGTACTAG,S513,TCGACTAG,PhiX\Illumina\RTA\Sequence\WholeGenomeFasta,,
020515DV2-K0049,020515DV2-K0049,20151008_Dengue,A03,N703,AGGCAGAA,S513,TCGACTAG,PhiX\Illumina\RTA\Sequence\WholeGenomeFasta,,'''
#TODO: need to use ngsdir / 'MiSeq' / etc
#sh.mkdir(ngsdir / 'RawData')
#sh.mkdir(readdata)
#sh.mkdir(ngsdir / 'ReadsBySample')
#TODO: mock sample_sheet_to_df or open
#ss_filename = ngsdir / 'RawData' / runname / 'SampleSheet.csv'
def make_ss_to_df(samples):
    data = [{ 'Sample_Name' : sample.subject, 'Sample_ID' : sample.subject } for sample in samples]
    return lambda _: miseq_sync.pd.DataFrame(data=data, columns=['Sample_Name', 'Sample_ID'])

@st.composite
def samples_strat(draw):
  Sample = namedtuple('Sample', ['subject', 'id'])
  sample_strat = st.tuples(st.text(), st.integers()).map(lambda x: Sample(*x))
  old_samples = draw(st.lists(sample_strat, max_size=10, unique_by=lambda x: x.id))
  new_samples = draw(st.lists(sample_strat, max_size=10, unique_by=lambda x: x.id))
  assume(len(set([s.id for s in (old_samples + new_samples)])) == len(old_samples + new_samples))
  return old_samples, new_samples

miseq_sync.sh = mock.MagicMock()

@given(st.integers(), st.text(), samples_strat())
def test_everything(runid, runname, sample_data):
  old_samples, new_samples = sample_data
  ngsdir = Path("NGSDIR/MiSeq")
  runfolder = ngsdir / 'ReadData' / runname
  issue2fastqs = {}
  miseq_sync.sh = mock.MagicMock()
  samplenames = [s.subject for s in old_samples + new_samples]
  read_files = [ runfolder / "{}.fastq".format(sn) for sn in samplenames ]
  for sample in old_samples + new_samples:
    name_files = [f for f in read_files if
                  f.basename().startswith(sample.subject)]
    issue_files = [miseq_sync.rename_issue_date(p, sample) for p in name_files]
    issue2fastqs[sample.id] = issue_files
    for src, dest in zip(name_files, issue_files):
      miseq_sync.sh.mv.assert_called_with(src, runfolder / dest)
  for sample in new_samples:
    miseq_sync.sh.mkdir.assert_called_with(ngsdir / 'ReadsBySample' / sample)
  assert miseq_sync.sh.mkdir.call_count == len(new_samples)
  for id, fastqs in issue2fastqs.items():
    for fq in fastqs:
      dest = ngsdir / 'ReadsBySample' / str(id) / fq
      miseq_sync.sh.ln.assert_called_with(runfolder / fq, dest, s=True)
  def flatten(seq):
    return list(itertools.chain.from_iterable(seq))
  assert miseq_sync.sh.ln.call_count == len(flatten(issue2fastqs.values()))
def mock_setup(runid, runname, old_samples, new_samples):
  miseq_sync.Redmine = mock.MagicMock()
  mock_R = mock.MagicMock()
  miseq_sync.cf = lambda x,k: x.cfs[k]
  samplelist = '\n'.join([s.name for s in old_samples + new_samples])
  mock_run = mock.MagicMock(cfs=[{'Run Name' : runname, 'SampleList' : samplelist}], id=runid)
  mock_R.issue.filter.return_value = old_samples
  run_ret = mock.MagicMock()
  run_ret.issues.get.return_value = mock_run
  mock_R.project.get.return_value = run_ret
  miseq_sync.Redmine.return_value = mock_R

# info needed
'''old samples (names, ids)
new samples (names, ids)
run name
sample list (old and new sample names)'''

# some way to test set_status
# miseq_sync.new_sample.return

def run_sh_ln(path):
  miseq_sync.sh.ln(path)

def test_mock_sh(mocker):
  #sh = mocker.patch('sh')
  path = '/foo/bar'
  run_sh_ln(path)
  miseq_sync.sh.ln.assert_called_with(path)

