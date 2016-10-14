import mock
import itertools
# Config = NamedTuple('Config', ['key', 'url', 'ngsdir', 'runissue'])

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
ngsdir = Path("NGSDIR/MiSeq")
#sh.mkdir(ngsdir / 'RawData')
#sh.mkdir(readdata)
#sh.mkdir(ngsdir / 'ReadsBySample')
#TODO: mock sample_sheet_to_df or open
ss_filename = ngsdir / 'RawData' / runname / 'SampleSheet.csv'
with open(ss_filename, 'w') as ss_out:
    ss_out.write(samplesheet_text)
def make_ss_to_df(data):
    return lambda _: pd.DataFrame(data=data, columns=['Sample_Name', 'Sample_ID'])

sh = mock.MagickMock()
issue2fastqs = {}
runfolder = ngsdir / 'ReadData' / runname
for sample in samples:
  name_files = [f for f in rd_files if f.basename().startswith(sample.subject)]
  issue_files = [rename_issue_date(p, sample) for p in name_files]
  issue2fastqs[sample.id] = issue_files
  for src, dest in zip(name_files, issue_files):
    sh.mv.assert_called_with(src, runfolder / dest)
for sample in new_samples:
  sh.mkdir.assert_called_with(ngsdir / 'ReadsBySample' / sample)
assert sh.mkdir.call_count == len(new_samples)
def flatten(seq):
    return list(itertools.chain.from_iterable(seq))
for id, fastqs in issue2fastqs.items():
    for fq in fastqs:
        dest = ngsdir / 'ReadsBySample' / str(id) / fq
        sh.ln.assert_called_with(runfolder / fq, dest, s=True)
    assert sh.ln.call_count == len(flatten(issue2fastqs.values()))


