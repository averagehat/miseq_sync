from redsample.defaults import defaults
from redsample.sequencerequest import SequenceRequest
import sys

def main( args ):
    if not args.key:
        print "Please set up your my.py file with your api key"
        sys.exit( 1 )
        
    sr = SequenceRequest( args.url, args.key )
    sr.DRY = args.dry
    sr.sync_requests()

def parse_args( ):
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--key',
        dest='key',
        default=defaults.get('KEY',''),
        help='API Key listed under My Account'
    )

    parser.add_argument(
        '--url',
        dest='url',
        default=defaults['URL'],
        help='URL to Redmine Instance'
    )

    parser.add_argument(
        '--dry',
        default=False,
        action='store_true',
        help='Just show requests that will be synced'
    )

    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
