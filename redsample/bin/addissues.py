from redsample import redminerest
import sys

def iter_samplesheet( sheetpath ):
    with open( sheetpath ) as fh:
        for line in fh:
            sample, pathogen = line.strip().split()
            # Skip commented out
            if sample.startswith('#'):
                continue
            yield sample, pathogen


def add_genome_subtasks( sheetpath ):
    for sample in iter_samplesheet( sheetpath ):
        issues = rest.get_issues( subject=sample )['issues']
        assert len(issues) == 1, "Returned more than 1 issue for {}: {}".format(sample,issues)
        issue = issues[-1]
        parent_id = issue['id']

        try:
            map_issue = rest.add_issue(
                project_id=PROJECT_ID,
                subject='{} Mapping'.format(sample),
                parent_issue_id=parent_id
            )
        except redminerest.DuplicateEntry:
            pass

        try:
            qc_issue = rest.add_issue(
                project_id=PROJECT_ID,
                subject='{} Final QC'.format(sample),
                parent_issue_id=parent_id
            )
        except redminerest.DuplicateEntry:
            pass

def parse_args( args=sys.argv[1:] ):
    import argparse
    parser = argparse.ArgumentParser(
        description='Sets up a new sequencing run by creating a new Sequencing Request issue ' \
            'as well as an issue for every sample name in the given sample sheet and then relating the two'
    )

    parser.add_argument(
        'samplesheet',
        help='Samplesheet that has 2 space separated columns, samplename pathogen'
    )

    parser.add_argument(
        'platform',
        choices=('MiSeq','Roche454','IonTorrent','Sanger'),
        help='Which platform the sequencing run will be for'
    )

    parser.add_argument(
        'seq_req_name',
        help='The name that the sequencing request will have(Subject)'
    )

    return parser.parse_args( args )

def main( args ):
    samples = Samples( URL, KEY )
    sampleissues = samples.add_samplesheet( args.samplesheet )
    samples.add_sequencing_request( args.seq_req_name, args.platform, sampleissues )

if __name__ == '__main__':
    main( parse_args() )
