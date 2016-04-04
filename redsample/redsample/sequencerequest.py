import redminerest
from defaults import defaults

class SequenceRequest( redminerest.Issues ):
    DRY = False
    def find_syncable( self ):
        '''
            @param project_id - Id of project that contains syncable sequence requests
            @param custom_field_id - ID of custom field to filter by(SamplesSynced)

            @returns a list of issues that can be synced(Have samples created and related to issue)
        '''
        kargs = {
            'project_id': self.SEQUENCE_REQUEST_PROJECT_ID,
            'tracker_id': self.NEW_SEQUENCE_REQUEST_TRACKER_ID,
            'cf_{}'.format(self.SAMPLESSYNCED_ID): 0
        }
        seqreqs = self.get_issues( **kargs )['issues']
        return seqreqs

    def get_sample_list( self, seq_request_issue ):
        sample_list = filter( lambda field: field['id'] == self.SAMPLELIST_ID, seq_request_issue['custom_fields'] )[0]['value']
        sample_list = sample_list.split()
        return sample_list

    def sync_sequence_request( self, seq_request_issue ):
        '''
            @param seq_request_issue - Issue json for a Sequence Request
        '''
        samplelist = self.get_sample_list( seq_request_issue )
        for sample in samplelist:
            self.relate_sample( sample, seq_request_issue )

        # Update sequence request issue so SamplesSynced is now 1
        self.set_samplessynced( seq_request_issue, True )

    def set_samplessynced( self, seq_request_issue, samplessynced=True ):
        '''
            @param seq_request_issue - sequenceing request json to update
            @param samplessynced - Can be 0,1,True,False but will be set to 0|1 in the json to indicate on or off
        '''
        # Find the custom field and update it
        for cusfield in seq_request_issue['custom_fields']:
            if cusfield['id'] == self.SAMPLESSYNCED_ID:
                # Update the field with int value
                cusfield['value'] = str( int(samplessynced) )
        # Now update the issue
        self.update_issue( seq_request_issue['id'], seq_request_issue )

    def relate_sample( self, sample, seq_request_issue ):
        '''
            @param sample - The name of the sample to relate to the sequence request
            @param seq_request_issue - Issue json of the sequence request to relate the sample to
        '''
        from samples import Samples
        s = Samples( self.url, self.key )
        created, sample_issue = s.get_or_create( sample )

        # Set the relation
        try:
            self.set_relation( seq_request_issue, 'blocks', sample_issue )
        except self.RelationExists as e:
            # Already created
            pass

    def sync_requests( self ):
        seq_requests = self.find_syncable()
        for req in seq_requests:
            if self.DRY:
                sub = req['subject']
                cf = req['custom_fields']
                platrun = [field['value'] for field in filter( lambda x: x['name'] in ('Platform','Run Name'), cf )]
                print 'Subject: \'' + sub + '\' ' + ':'.join( platrun )
            else:
                if raw_input( "Sync {}? ".format(req['subject']) ).lower() in ('y','yes'):
                    self.sync_sequence_request( req )
