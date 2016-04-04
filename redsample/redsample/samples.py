import urllib2
import json
import redminerest
from defaults import defaults
import re

class Samples( redminerest.Issues ):
    ''' Class to handle Sample Tracking '''
    def filter_issues( self, original, issues ):
        '''
        Filter issues down to only what was actually looked for
        '''
        orig = original.upper().replace('-','_').replace('/','_').replace(' ','_')
        fnd = []
        for iss in issues:
            isssub = iss['subject']
            isssub = isssub.upper().replace('-','_').replace('/','_').replace(' ','_')
            if orig == isssub:
                fnd.append( iss )
        return fnd

    def find_sample( self, **kwargs ):
        origsubject = kwargs['subject']
        kwargs['subject'] = '~' + re.sub( r'[!"#$%&\'()*+,-\./:;<=>?@\[\\\]^`{|}~]', '_', origsubject )
        issues = self.get_issues( **kwargs )['issues']
        if issues:
            return self.filter_issues( origsubject, issues )

        if origsubject.startswith('PR'):
            # Search by PRName using ~
            pru = origsubject.upper().replace('-','_')
            args = {
                'project_id': defaults['SAMPLE_PROJECT_ID'],
                'cf_{}'.format(defaults['PRNAME_ID']): '~{}'.format(pru),
            }
            issues = self.get_issues( **args )['issues']
            return issues
        else:
            return []

    def add_sample( self, samplename, **kwargs ):
        try:
            issue = self.add_issue(
                subject=samplename,
                pathogen=kwargs.get('pathogen','Unk'),
                project_id=self.SAMPLE_PROJECT_ID,
                status_id=self.NEW_SAMPLE_STATUS_ID,
                tracker_id=self.NEW_SAMPLE_TRACKER_ID
            )
            return (True,issue)
        except self.DuplicateEntry as e:
            return (False,e.dupissue)

    def get_or_create( self, samplename, **kwargs ):
        '''
            Create new sample or get existing if it already exists
        
            @returns Tuple of (True|False,issue) where True means that issue was created
                and False means it was not
        '''
        s = self.add_sample( samplename, **kwargs )
        if s[0]:
            return (True,s[1])
        else:
            #return (False,self.get_issues( subject=samplename )['issues'][0])
            return (False,s[1][0])

    def add_sequencing_request( self, seqrequestname, platform, sampleissues, description='' ):
        # List of samples to add to custom field
        samplelist = '\r\n'.join( [sample['subject'] for sample in sampleissues] )
        seq_req_issue = None
        try:
            seq_req_issue = self.add_issue(
                subject=seqrequestname,
                description=description,
                custom_fields=[
                    {'id':self.SAMPLELIST_ID,'value':samplelist},
                    {'id':self.PLATFORM_ID,'value':platform}
                ],
                project_id=self.SEQUENCE_REQUEST_PROJECT_ID,
                status_id=self.NEW_SEQUENCE_REQUEST_STATUS_ID,
                tracker_id=self.NEW_SEQUENCE_REQUEST_TRACKER_ID
            )
        except urllib2.HTTPError as e:
            body = e.read()
            js = json.loads( body )
            print js['errors']
            return
        except self.DuplicateEntry:
            seq_req_issue = self.get_issues( subject=seqrequestname )['issues'][0]
                
        for sample in sampleissues:
            try:
                self.set_relation( seq_req_issue, 'blocks', sample )
            except urllib2.HTTPError as e:
                # Probably already exists
                continue
                #body = e.read()
                #js = json.loads( body )

    def add_samplesheet( self, sheetpath ):
        '''
            Adds all issues not commented out and not already added
        '''
        sample_issues = []
        for sample, pathogen in iter_samplesheet( sheetpath ):
            created, iss = self.add_sample( sample, pathogen=pathogen )
            if created:
                print "Inserted new sample {}".format(sample)
            if iss is None:
                iss = self.get_issues( subject=sample )['issues'][0]
            sample_issues.append( iss )
        return sample_issues

