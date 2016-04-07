#!/usr/bin/env python

from redsample.samples import Samples
from redsample.defaults import defaults
import sys

def main( args ):
    # Hacky McHackerton here
    defaults['KEY'] = args.key
    if args.issueid:
        print "SampleName,IssueID"
        mapping_for_samples( args.samplename, args.create )
    else:
        print "IssueID,SampleName"
        mapping_for_issueids( args.samplename )

def mapping_for_samples( samplenames, create=False ):
    '''
    Get a mapping of samplename,issueid
    If create is True and there is no issue for the sample then create it otherwise
    return None
    '''
    samplerest = Samples( defaults['URL'], defaults['KEY'] )
    for sample in samplenames:
        sys.stdout.write( "{},{}\n".format( *sample_to_id( sample, samplerest, create ) ) )
        sys.stdout.flush()

def sample_to_id( sample, rest, create=False ):
    if create:
        _, si = rest.get_or_create( sample )
        si = (si,)
    else:
        si = rest.find_sample( subject=sample )

    from pprint import pformat
    assert len(si) <= 1, 'More than one issue returned for {}: {}'.format(sample,pformat(si))
    if len(si) == 1:
        si = si[0]['id']
    else:
        # No result
        si = ''
    return (si,sample)

def mapping_for_issueids( issueids ):
    samplerest = Samples( defaults['URL'], defaults['KEY'] )
    for id in issueids:
        try:
            issue = samplerest.get_issue_by_id( id )
        except samplerest.InvalidIssue:
            issue = {'subject': ''}
        sys.stdout.write( '{},{}\n'.format(id,issue['subject']) )
        sys.stdout.flush()

def parse_args( args=sys.argv[1:] ):
    import argparse
    parser = argparse.ArgumentParser(
        description='''Return issue id's for given samplenames'''
    )

    parser.add_argument(
        'samplename',
        nargs='+',
        help='Samplename or list of samplenames to get id\'s for'
    )

    parser.add_argument(
        '--key',
        required=True,
        help='API access key listed under My account in Redmine'
    )

    parser.add_argument(
        '--issueid',
        action='store_false',
        default=True,
        help='Given list is a list of issue ids not samplenames'
    )

    parser.add_argument(
        '--create',
        action='store_true',
        default=False,
        help='Create issues for samplenames that do not exist'
    )

    return parser.parse_args( args )
    
if __name__ == "__main__":
    main(parse_args())
